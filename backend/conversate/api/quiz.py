import random
from datetime import timedelta

from flask import Blueprint, abort, jsonify
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError

from ..auth import require_auth
from ..extensions import db
from ..models import QuizAttempt, User
from ..quiz_data import QUIZ_WORDS
from .common import json_body, resolve_me, utcnow

quiz_bp = Blueprint('quiz_bp', __name__)

# The quiz page states these limits, MAX_PAUSE_CREDIT_SECONDS, and the number
# of QUIZ_WORDS; keep it in step.
QUIZ_TIME_LIMIT_SECONDS = 250
MAX_QUIZ_PAUSES = 1
# The UI shows each answer for 500ms, so faster answering is a script. This
# only slows one down.
MIN_SECONDS_PER_ANSWER = 0.5
# The most pause time kept off the quiz clock; anything longer counts.
MAX_PAUSE_CREDIT_SECONDS = 120


def _build_quiz():
    words = list(QUIZ_WORDS)
    random.shuffle(words)
    # Draw distractors from the least-used words, so they're spread evenly
    # across the quiz.
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
    return db.session.scalars(
        select(QuizAttempt).where(QuizAttempt.user_id == user_id)
    ).one_or_none()


def _require_attempt(user_id):
    attempt = _find_attempt(user_id)
    if attempt is None:
        abort(409, description='No quiz in progress; call /api/me/quiz/start first')
    return attempt


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
        # A simultaneous first start inserted first; the unique index on
        # user_id lets only one through.
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
    index = body.get('index')
    if not isinstance(index, int) or isinstance(index, bool):
        return jsonify(error='index must be an integer'), 400

    attempt = _require_attempt(record.id)
    if attempt.paused_at is not None:
        return jsonify(error='Quiz is paused; call /api/me/quiz/resume first'), 409
    if _seconds_remaining(attempt.started_at) <= 0:
        return jsonify(error='Time is up; call /api/me/quiz/submit'), 409
    if attempt.next_index >= len(attempt.quiz_state):
        return jsonify(error='All questions have already been answered'), 409
    if index != attempt.next_index:
        return jsonify(error='index does not match the current question'), 409
    if (utcnow() - attempt.started_at).total_seconds() < index * MIN_SECONDS_PER_ANSWER:
        return jsonify(error='Answering too fast'), 429

    correct = body.get('answer') == attempt.quiz_state[index]['correct']

    # Check and advance next_index in one statement, so concurrent guesses at
    # one question can't all score.
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
    attempt = _require_attempt(record.id)
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
    attempt = _require_attempt(record.id)
    if attempt.paused_at is not None:
        # Move the start forward by the pause, up to MAX_PAUSE_CREDIT_SECONDS,
        # so it doesn't count against the clock.
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
    attempt = _require_attempt(record.id)

    score = attempt.correct_count
    time_seconds = int(
        QUIZ_TIME_LIMIT_SECONDS - _seconds_remaining(attempt.started_at, attempt.paused_at)
    )
    db.session.delete(attempt)

    # One conditional update, so concurrent submits can't replace a better
    # score with a stale one.
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
    # Only the columns shown. The filter and sort match ix_account_leaderboard,
    # so Postgres reads the top rows straight from the index.
    users = db.session.execute(
        select(User.username, User.quiz_best_score, User.quiz_best_time_seconds)
        .where(User.quiz_best_score.is_not(None))
        # id breaks ties on score and time, so the order is stable.
        .order_by(User.quiz_best_score.desc(), User.quiz_best_time_seconds.asc(), User.id.asc())
        .limit(100)
    ).all()
    rows = [
        {
            'username': u.username,
            'score': u.quiz_best_score,
            'time_seconds': u.quiz_best_time_seconds,
        }
        for u in users
    ]
    return jsonify(rows), 200
