import random

from flask import Blueprint, jsonify

from ..extensions import db
from ..models import User, QuizAttempt
from ..quiz_data import QUIZ_WORDS
from ..auth import require_auth
from .common import _json_body, _resolve_me, _utcnow

quiz_bp = Blueprint('quiz_bp', __name__)

TOTAL_QUIZ_QUESTIONS = len(QUIZ_WORDS)
QUIZ_TIME_LIMIT_SECONDS = 250
MAX_QUIZ_PAUSES = 1


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


def _seconds_remaining(started_at, at_time=None):
    elapsed = ((at_time or _utcnow()) - started_at).total_seconds()
    return max(0, QUIZ_TIME_LIMIT_SECONDS - elapsed)


def _find_attempt(user_id):
    return db.session.query(QuizAttempt).filter(
        QuizAttempt.user_id == user_id
    ).one_or_none()


@quiz_bp.route('/api/me/quiz/start', methods=['POST'])
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


@quiz_bp.route('/api/me/quiz/answer', methods=['POST'])
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


@quiz_bp.route('/api/me/quiz/pause', methods=['POST'])
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


@quiz_bp.route('/api/me/quiz/resume', methods=['POST'])
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


@quiz_bp.route('/api/me/quiz/submit', methods=['POST'])
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


@quiz_bp.route('/api/leaderboard', methods=['GET'])
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
