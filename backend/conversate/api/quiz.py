import random
from datetime import timedelta

from flask import Blueprint, jsonify
from sqlalchemy import update
from sqlalchemy.exc import IntegrityError

from ..auth import require_auth
from ..extensions import db
from ..models import QuizAttempt, User
from ..quiz_data import QUIZ_WORDS
from .common import json_body, resolve_me, utcnow

quiz_bp = Blueprint('quiz_bp', __name__)

QUIZ_TIME_LIMIT_SECONDS = 250
MAX_QUIZ_PAUSES = 1
# A human never answers this fast — the UI itself holds each answer on
# screen for 500ms before advancing. This slows down a script racing
# through the quiz without a real answer key; it can't stop one, since
# a script can simply pace itself slower than this.
MIN_SECONDS_PER_ANSWER = 0.5
# How much of a pause actually gets excluded from the 250s clock. Longer
# than this and the clock resumes running anyway, capping how much total
# time a pause can buy back.
MAX_PAUSE_CREDIT_SECONDS = 120


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
    elapsed = ((at_time or utcnow()) - started_at).total_seconds()
    return max(0, QUIZ_TIME_LIMIT_SECONDS - elapsed)


def _find_attempt(user_id):
    return db.session.query(QuizAttempt).filter(QuizAttempt.user_id == user_id).one_or_none()


@quiz_bp.route('/api/me/quiz/start', methods=['POST'])
@require_auth
@resolve_me
def start_quiz(record):
    questions = _build_quiz()
    started_at = utcnow()

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
    try:
        db.session.commit()
    except IntegrityError:
        # Two simultaneous first-time starts both saw no existing attempt and
        # both tried to insert one; the unique index on user_id lets only one
        # through.
        db.session.rollback()
        return jsonify(error='Quiz already starting'), 409

    client_questions = [{'it': q['it'], 'choices': q['choices']} for q in questions]
    seconds_remaining = _seconds_remaining(started_at)
    return jsonify(
        questions=client_questions,
        seconds_remaining=seconds_remaining,
        pauses_remaining=MAX_QUIZ_PAUSES,
    ), 200


@quiz_bp.route('/api/me/quiz/answer', methods=['POST'])
@require_auth
@resolve_me
def answer_quiz(record):
    body = json_body()
    if body is None:
        return jsonify(error='Request body must be a JSON object'), 400
    index = body.get('index')
    if not isinstance(index, int) or isinstance(index, bool):
        return jsonify(error='index must be an integer'), 400

    attempt = _find_attempt(record.id)
    if attempt is None:
        return jsonify(error='No quiz in progress; call /api/me/quiz/start first'), 409
    if attempt.paused_at is not None:
        return jsonify(error='Quiz is paused; call /api/me/quiz/resume first'), 409
    if _seconds_remaining(attempt.started_at) <= 0:
        return jsonify(error='Time is up; call /api/me/quiz/submit'), 409
    if (utcnow() - attempt.started_at).total_seconds() < index * MIN_SECONDS_PER_ANSWER:
        return jsonify(error='Answering too fast'), 429
    if attempt.next_index >= len(attempt.quiz_state):
        return jsonify(error='All questions have already been answered'), 409
    if index != attempt.next_index:
        return jsonify(error='index does not match the current question'), 409

    correct = body.get('answer') == attempt.quiz_state[index]['correct']

    # Checking next_index and incrementing it must be one atomic operation:
    # separate read-then-write steps let concurrent requests for the same
    # index all pass the check before any of them commits, so every
    # simultaneous guess would score.
    result = db.session.execute(
        update(QuizAttempt)
        .where(
            QuizAttempt.id == attempt.id,
            QuizAttempt.next_index == index,
            QuizAttempt.paused_at.is_(None),
        )
        .values(
            next_index=QuizAttempt.next_index + 1,
            correct_count=QuizAttempt.correct_count + int(correct),
        )
    )
    db.session.commit()
    if result.rowcount == 0:
        return jsonify(error='index does not match the current question'), 409

    return jsonify(correct=correct), 200


@quiz_bp.route('/api/me/quiz/pause', methods=['POST'])
@require_auth
@resolve_me
def pause_quiz(record):
    attempt = _find_attempt(record.id)
    if attempt is None:
        return jsonify(error='No quiz in progress; call /api/me/quiz/start first'), 409
    if attempt.paused_at is None:
        if attempt.pauses_used >= MAX_QUIZ_PAUSES:
            return jsonify(error='No pauses remaining'), 409
        attempt.paused_at = utcnow()
        attempt.pauses_used += 1
        db.session.commit()
    return jsonify(
        seconds_remaining=_seconds_remaining(attempt.started_at, attempt.paused_at),
        pauses_remaining=MAX_QUIZ_PAUSES - attempt.pauses_used,
    ), 200


@quiz_bp.route('/api/me/quiz/resume', methods=['POST'])
@require_auth
@resolve_me
def resume_quiz(record):
    attempt = _find_attempt(record.id)
    if attempt is None:
        return jsonify(error='No quiz in progress; call /api/me/quiz/start first'), 409
    if attempt.paused_at is not None:
        # Shift the anchor forward by however long the pause lasted, so the
        # paused time is never counted against the 250s cap — but only up to
        # a cap, so a pause can't be stretched out into unlimited extra time.
        paused_duration = min(
            (utcnow() - attempt.paused_at).total_seconds(), MAX_PAUSE_CREDIT_SECONDS
        )
        attempt.started_at += timedelta(seconds=paused_duration)
        attempt.paused_at = None
        db.session.commit()
    return jsonify(
        seconds_remaining=_seconds_remaining(attempt.started_at),
        pauses_remaining=MAX_QUIZ_PAUSES - attempt.pauses_used,
    ), 200


@quiz_bp.route('/api/me/quiz/submit', methods=['POST'])
@require_auth
@resolve_me
def submit_quiz(record):
    attempt = _find_attempt(record.id)
    if attempt is None:
        return jsonify(error='No quiz in progress; call /api/me/quiz/start first'), 409

    score = attempt.correct_count
    time_seconds = int(
        QUIZ_TIME_LIMIT_SECONDS - _seconds_remaining(attempt.started_at, attempt.paused_at)
    )
    db.session.delete(attempt)

    # Same atomicity concern as /answer: two concurrent submits must not
    # both read the old best, decide "I'm better", and write — the second
    # write would silently clobber the first with a stale is_new_best.
    result = db.session.execute(
        update(User)
        .where(
            User.id == record.id,
            (User.quiz_best_score.is_(None))
            | (User.quiz_best_score < score)
            | ((User.quiz_best_score == score) & (User.quiz_best_time_seconds > time_seconds)),
        )
        .values(quiz_best_score=score, quiz_best_time_seconds=time_seconds)
    )
    db.session.commit()
    is_new_best = result.rowcount > 0

    return jsonify(score=score, time_seconds=time_seconds, is_new_best=is_new_best), 200


@quiz_bp.route('/api/leaderboard', methods=['GET'])
@require_auth
def leaderboard():
    # Only the three columns the response uses, not whole User rows; the
    # filter and sort match ix_user_leaderboard, so Postgres can read the top
    # rows straight off the index instead of scanning and sorting the table.
    users = (
        db.session.query(User.username, User.quiz_best_score, User.quiz_best_time_seconds)
        .filter(User.quiz_best_score.isnot(None))
        # id as a final tiebreak: without it, two rows tied on both score and
        # time have no defined relative order, so the leaderboard could show
        # them in either order from one request to the next.
        .order_by(User.quiz_best_score.desc(), User.quiz_best_time_seconds.asc(), User.id.asc())
        .limit(100)
        .all()
    )
    rows = [
        {
            'username': u.username,
            'score': u.quiz_best_score,
            'time_seconds': u.quiz_best_time_seconds,
        }
        for u in users
    ]
    return jsonify(rows), 200
