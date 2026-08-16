import random
import re
from datetime import datetime, timezone
from functools import wraps

from flask import Blueprint, jsonify, request, g, current_app
from sqlalchemy.exc import IntegrityError

from . import google_api
from .extensions import db
from .models import User, QuizAttempt
from .quiz_data import QUIZ_WORDS
from .auth import require_auth

api_bp = Blueprint('api_bp', __name__)


@api_bp.route('/health')
def health():
    return jsonify(status='ok'), 200

MIN_USERNAME_LENGTH = 3
MAX_USERNAME_LENGTH = 100
MAX_EMAIL_LENGTH = 100
_EMAIL_RE = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')
# Usernames appear in a URL path (the availability route), so restrict them to
# characters that are unambiguous as a path segment — no '/', space, or '?'.
_USERNAME_RE = re.compile(r'^[A-Za-z0-9_.-]+$')
# Must match the lesson count in frontend/src/data/lessons.js, or new lessons 400 on completion.
TOTAL_LESSONS = 10
VALID_LESSON_IDS = frozenset(range(1, TOTAL_LESSONS + 1))
TRANSLATE_LANGUAGES = frozenset({'en', 'it'})
MAX_TRANSLATE_TEXT_LENGTH = 5000
TTS_VOICES = {
    'en': {'languageCode': 'en-US', 'name': 'en-US-Wavenet-D'},
    'it': {'languageCode': 'it-IT', 'name': 'it-IT-Wavenet-A'},
}
MAX_TTS_TEXT_LENGTH = 5000  # bytes; Cloud Text-to-Speech's synchronous synthesize limit
STT_LANGUAGES = {'en': 'en-US', 'it': 'it-IT'}
STT_ENCODINGS = {'audio/webm;codecs=opus': 'WEBM_OPUS'}
MAX_STT_AUDIO_BYTES = 1_000_000
TOTAL_QUIZ_QUESTIONS = len(QUIZ_WORDS)
QUIZ_TIME_LIMIT_SECONDS = 250
MAX_QUIZ_PAUSES = 1


def _json_body():
    body = request.get_json(silent=True)
    return body if isinstance(body, dict) else None


def _username_error(name):
    if not name:
        return 'user_name is required'
    if len(name) < MIN_USERNAME_LENGTH:
        return 'user_name must be at least %d characters' % MIN_USERNAME_LENGTH
    if len(name) > MAX_USERNAME_LENGTH:
        return 'user_name must be at most %d characters' % MAX_USERNAME_LENGTH
    if not _USERNAME_RE.match(name):
        return 'user_name may only contain letters, numbers, and _ . -'
    return None


def _find_user(sub):
    return db.session.query(User).filter(User.auth0_sub == sub).one_or_none()


def _body_email(body):
    email = (body.get('email') or '').strip()
    if not _EMAIL_RE.match(email) or len(email) > MAX_EMAIL_LENGTH:
        return None
    return email


def _resolve_me(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        record = _find_user(g.current_user_sub)
        if record is None:
            return jsonify(error='Unknown resource'), 404
        return f(record, *args, **kwargs)
    return decorated


def _utcnow():
    # Naive UTC, matching the naive DateTime column quiz_state.started_at is
    # stored in and compared against.
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _build_quiz():
    words = list(QUIZ_WORDS)
    random.shuffle(words)
    # Picking distractors independently per question lets popular words get
    # drawn far more often than others by chance. Track how many times each
    # word has been used as a distractor and always draw from the
    # least-used ones, so usage stays balanced across the whole quiz instead
    # of clustering on a handful of repeats.
    usage = {w['en']: 0 for w in QUIZ_WORDS}
    questions = []
    for word in words:
        others = [w for w in QUIZ_WORDS if w['en'] != word['en']]
        random.shuffle(others)
        others.sort(key=lambda w: usage[w['en']])
        distractors = others[:3]
        for d in distractors:
            usage[d['en']] += 1
        choices = [word['en']] + [d['en'] for d in distractors]
        random.shuffle(choices)
        questions.append({'it': word['it'], 'choices': choices, 'correct': word['en']})
    return questions


def _username_taken(name, exclude_id=None):
    query = db.session.query(User.id).filter(
        db.func.lower(User.user_name) == name.lower()
    )
    if exclude_id is not None:
        query = query.filter(User.id != exclude_id)
    return query.first() is not None


def _validate_username(name, conflict_message, exclude_id=None):
    """Shared by create and rename: returns an error response, or None."""
    name_error = _username_error(name)
    if name_error:
        return jsonify(error=name_error), 400
    if _username_taken(name, exclude_id=exclude_id):
        return jsonify(error=conflict_message), 409
    return None


@api_bp.route('/api/me', methods=['POST'])
@require_auth
def create_me():
    sub = g.current_user_sub
    body = _json_body()
    if body is None:
        return jsonify(error='Request body must be a JSON object'), 400
    user_name = (body.get('user_name') or '').strip()
    email = _body_email(body)
    if email is None:
        return jsonify(error='A valid email is required'), 400
    if _find_user(sub) is not None:
        return jsonify(error='User already exists'), 409
    error = _validate_username(user_name, 'User already exists')
    if error:
        return error
    new_user = User(sub, email, user_name)
    db.session.add(new_user)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify(error='User already exists'), 409
    return jsonify(new_user.serialize()), 201


@api_bp.route('/api/me', methods=['GET'])
@require_auth
@_resolve_me
def get_me(record):
    return jsonify(record.serialize()), 200


@api_bp.route('/api/me', methods=['PUT'])
@require_auth
@_resolve_me
def update_me(record):
    body = _json_body()
    if body is None:
        return jsonify(error='Request body must be a JSON object'), 400
    new_name = (body.get('user_name') or '').strip()
    error = _validate_username(new_name, 'user_name already exists',
                               exclude_id=record.id)
    if error:
        return error
    record.user_name = new_name
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify(error='user_name already exists'), 409
    return jsonify(record.serialize()), 200


@api_bp.route('/api/me/lessons/<int:lesson_id>', methods=['POST'])
@require_auth
@_resolve_me
def complete_my_lesson(record, lesson_id):
    if lesson_id not in VALID_LESSON_IDS:
        return jsonify(error='Invalid lesson id'), 400
    completed = list(record.lessons_completed or [])
    if lesson_id not in completed:
        completed.append(lesson_id)
        record.lessons_completed = completed
        db.session.commit()
    return jsonify(record.serialize()), 200


@api_bp.route('/api/me/reset', methods=['POST'])
@require_auth
@_resolve_me
def reset_me(record):
    record.lessons_completed = []
    record.quiz_best_score = None
    record.quiz_best_time_seconds = None
    db.session.commit()
    return jsonify(record.serialize()), 200


@api_bp.route('/api/usernames/<user_name>', methods=['GET'])
@require_auth
def username_available(user_name):
    user_name = user_name.strip()
    name_error = _username_error(user_name)
    if name_error:
        return jsonify(error=name_error), 400
    if _username_taken(user_name):
        return jsonify(error='user_name already exists'), 409
    return jsonify(message='Success'), 200


def _seconds_remaining(started_at, at_time=None):
    elapsed = ((at_time or _utcnow()) - started_at).total_seconds()
    return max(0, QUIZ_TIME_LIMIT_SECONDS - elapsed)


def _find_attempt(user_id):
    return db.session.query(QuizAttempt).filter(
        QuizAttempt.user_id == user_id
    ).one_or_none()


@api_bp.route('/api/me/quiz/start', methods=['POST'])
@require_auth
@_resolve_me
def start_quiz(record):
    questions = _build_quiz()
    started_at = _utcnow()

    attempt = _find_attempt(record.id)
    if attempt is None:
        attempt = QuizAttempt(user_id=record.id)
        db.session.add(attempt)
    attempt.started_at = started_at
    attempt.quiz_state = questions
    attempt.next_index = 0
    attempt.correct_count = 0
    attempt.paused_at = None
    attempt.pauses_used = 0
    db.session.commit()

    client_questions = [{'it': q['it'], 'choices': q['choices']} for q in questions]
    seconds_remaining = _seconds_remaining(started_at)
    return jsonify(
        questions=client_questions,
        seconds_remaining=seconds_remaining,
        pauses_remaining=MAX_QUIZ_PAUSES,
    ), 200


@api_bp.route('/api/me/quiz/answer', methods=['POST'])
@require_auth
@_resolve_me
def answer_quiz(record):
    body = _json_body()
    if body is None:
        return jsonify(error='Request body must be a JSON object'), 400
    index = body.get('index')
    if not isinstance(index, int) or isinstance(index, bool):
        return jsonify(error='index must be an integer'), 400

    attempt = _find_attempt(record.id)
    if attempt is None:
        return jsonify(error='No quiz in progress; call /api/me/quiz/start first'), 409
    if _seconds_remaining(attempt.started_at) <= 0:
        return jsonify(error='Time is up; call /api/me/quiz/submit'), 409
    if attempt.next_index >= len(attempt.quiz_state):
        return jsonify(error='All questions have already been answered'), 409
    if index != attempt.next_index:
        return jsonify(error='index does not match the current question'), 409

    correct = body.get('answer') == attempt.quiz_state[index]['correct']
    attempt.next_index += 1
    if correct:
        attempt.correct_count += 1
    db.session.commit()

    return jsonify(correct=correct), 200


@api_bp.route('/api/me/quiz/pause', methods=['POST'])
@require_auth
@_resolve_me
def pause_quiz(record):
    attempt = _find_attempt(record.id)
    if attempt is None:
        return jsonify(error='No quiz in progress; call /api/me/quiz/start first'), 409
    if attempt.paused_at is None:
        if attempt.pauses_used >= MAX_QUIZ_PAUSES:
            return jsonify(error='No pauses remaining'), 409
        attempt.paused_at = _utcnow()
        attempt.pauses_used += 1
        db.session.commit()
    return jsonify(
        seconds_remaining=_seconds_remaining(attempt.started_at, attempt.paused_at),
        pauses_remaining=MAX_QUIZ_PAUSES - attempt.pauses_used,
    ), 200


@api_bp.route('/api/me/quiz/resume', methods=['POST'])
@require_auth
@_resolve_me
def resume_quiz(record):
    attempt = _find_attempt(record.id)
    if attempt is None:
        return jsonify(error='No quiz in progress; call /api/me/quiz/start first'), 409
    if attempt.paused_at is not None:
        # Shift the anchor forward by however long the pause lasted, so the
        # paused time is never counted against the 250s cap.
        attempt.started_at += _utcnow() - attempt.paused_at
        attempt.paused_at = None
        db.session.commit()
    return jsonify(
        seconds_remaining=_seconds_remaining(attempt.started_at),
        pauses_remaining=MAX_QUIZ_PAUSES - attempt.pauses_used,
    ), 200


@api_bp.route('/api/me/quiz/submit', methods=['POST'])
@require_auth
@_resolve_me
def submit_quiz(record):
    attempt = _find_attempt(record.id)
    if attempt is None:
        return jsonify(error='No quiz in progress; call /api/me/quiz/start first'), 409

    score = attempt.correct_count
    time_seconds = int(
        QUIZ_TIME_LIMIT_SECONDS - _seconds_remaining(attempt.started_at, attempt.paused_at)
    )
    db.session.delete(attempt)

    is_new_best = (
        record.quiz_best_score is None
        or score > record.quiz_best_score
        or (score == record.quiz_best_score and time_seconds < record.quiz_best_time_seconds)
    )
    if is_new_best:
        record.quiz_best_score = score
        record.quiz_best_time_seconds = time_seconds
    db.session.commit()

    return jsonify(
        score=score, time_seconds=time_seconds, is_new_best=is_new_best
    ), 200


@api_bp.route('/api/leaderboard', methods=['GET'])
@require_auth
def leaderboard():
    users = (
        db.session.query(User)
        .filter(User.quiz_best_score.isnot(None))
        .order_by(User.quiz_best_score.desc(), User.quiz_best_time_seconds.asc())
        .limit(100)
        .all()
    )
    rows = [
        {
            'user_name': u.user_name,
            'score': u.quiz_best_score,
            'time_seconds': u.quiz_best_time_seconds,
        }
        for u in users
    ]
    return jsonify(rows), 200


@api_bp.route('/api/translate', methods=['POST'])
@require_auth
def translate_text():
    body = _json_body()
    if body is None:
        return jsonify(error='Request body must be a JSON object'), 400
    text = (body.get('text') or '').strip()
    source = body.get('source')
    target = body.get('target')
    if not text or len(text) > MAX_TRANSLATE_TEXT_LENGTH:
        return jsonify(
            error='text is required and must be at most %d characters' % MAX_TRANSLATE_TEXT_LENGTH
        ), 400
    if source not in TRANSLATE_LANGUAGES or target not in TRANSLATE_LANGUAGES:
        return jsonify(
            error='source and target must be one of: %s' % ', '.join(sorted(TRANSLATE_LANGUAGES))
        ), 400

    try:
        data = google_api.post(google_api.TRANSLATE_URL, {
            'q': text,
            'source': source,
            'target': target,
            'format': 'text',
        })
        translated = data['data']['translations'][0]['translatedText']
    except (google_api.GoogleServiceError, KeyError, IndexError, TypeError) as e:
        current_app.logger.warning('Translation request failed: %s', e)
        return jsonify(error='Translation service unavailable'), 502

    return jsonify(translatedText=translated), 200


@api_bp.route('/api/tts', methods=['POST'])
@require_auth
def synthesize_speech():
    body = _json_body()
    if body is None:
        return jsonify(error='Request body must be a JSON object'), 400
    text = (body.get('text') or '').strip()
    voice = TTS_VOICES.get(body.get('language'))
    if not text or len(text.encode('utf-8')) > MAX_TTS_TEXT_LENGTH:
        return jsonify(
            error='text is required and must be at most %d characters' % MAX_TTS_TEXT_LENGTH
        ), 400
    if voice is None:
        return jsonify(
            error='language must be one of: %s' % ', '.join(sorted(TTS_VOICES))
        ), 400

    try:
        data = google_api.post(google_api.TTS_URL, {
            'input': {'text': text},
            'voice': voice,
            'audioConfig': {'audioEncoding': 'MP3'},
        })
        audio_content = data['audioContent']
    except (google_api.GoogleServiceError, KeyError, TypeError) as e:
        current_app.logger.warning('Speech synthesis request failed: %s', e)
        return jsonify(error='Speech synthesis service unavailable'), 502

    return jsonify(audioContent=audio_content), 200


@api_bp.route('/api/stt', methods=['POST'])
@require_auth
def transcribe_speech():
    body = _json_body()
    if body is None:
        return jsonify(error='Request body must be a JSON object'), 400
    audio_b64 = body.get('audio')
    encoding = STT_ENCODINGS.get(body.get('mimeType'))
    language_code = STT_LANGUAGES.get(body.get('language'))
    if not audio_b64 or encoding is None or language_code is None:
        return jsonify(error='audio, a supported mimeType, and language are required'), 400
    if len(audio_b64) > MAX_STT_AUDIO_BYTES * 4 // 3:
        return jsonify(error='audio is too large'), 400

    try:
        data = google_api.post(google_api.STT_URL, {
            'config': {'encoding': encoding, 'languageCode': language_code},
            'audio': {'content': audio_b64},
        })
    except google_api.GoogleServiceError as e:
        current_app.logger.warning('Transcription request failed: %s', e)
        return jsonify(error='Speech recognition service unavailable'), 502

    results = data.get('results') or []
    if not results:
        return jsonify(error='No speech detected'), 422
    try:
        transcript = results[0]['alternatives'][0]['transcript']
    except (KeyError, IndexError, TypeError) as e:
        current_app.logger.warning('Unexpected transcription response shape: %s', e)
        return jsonify(error='Speech recognition service unavailable'), 502

    return jsonify(transcript=transcript), 200
