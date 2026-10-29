import random

from flask import Blueprint, abort, jsonify, make_response, request
from sqlalchemy import delete, select, update
from sqlalchemy.exc import IntegrityError

from ..auth import require_auth
from ..extensions import db
from ..models import QuizAttempt, User
from ..quiz_data import QUIZ_WORDS
from .common import json_body, resolve_me, utcnow

quiz_bp = Blueprint('quiz_bp', __name__)

QUIZ_TIME_LIMIT_SECONDS = 250
MAX_QUIZ_PAUSES = 1
# The UI shows each answer for 500ms, so faster answering is a script. This
# only slows one down.
MIN_SECONDS_PER_ANSWER = 0.5


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


def _discard_attempt(user_id):
    # Separate so a test can slip a rival start in before ours commits.
    db.session.execute(delete(QuizAttempt).where(QuizAttempt.user_id == user_id))


def _require_attempt(user_id, body):
    """The user's quiz in progress, which body must name by attempt_id: a
    later start replaces it, and a tab still on the old one is told so
    instead of answering into the new one."""
    attempt = _find_attempt(user_id)
    if attempt is None:
        abort(409, description='No quiz in progress; call /api/me/quiz/start first')
    attempt_id = body.get('attempt_id')
    if not isinstance(attempt_id, int) or isinstance(attempt_id, bool):
        abort(400, description='attempt_id must be an integer')
    if attempt_id != attempt.id:
        # The frontend checks the code and drops the old quiz.
        abort(
            make_response(jsonify(error='A newer start replaced this quiz', code='replaced'), 409)
        )
    return attempt


def _require_timed(attempt):
    if attempt.practice:
        abort(409, description='A practice quiz has no timer')


def _out_of_sync():
    # The frontend checks the code: an answer sent again after its reply was
    # lost gets this, and the quiz moves on instead of ending.
    return jsonify(error='index does not match the current question', code='out_of_sync'), 409


def _practice_requested():
    """Whether start was asked for a practice quiz. The body is optional."""
    if not request.get_data():
        return False
    practice = json_body().get('practice', False)
    if not isinstance(practice, bool):
        abort(400, description='practice must be a boolean')
    return practice


@quiz_bp.route('/api/me/quiz/start', methods=['POST'])
@require_auth
@resolve_me
def start_quiz(record):
    practice = _practice_requested()
    questions = _build_quiz()
    started_at = utcnow()

    # A new row per start, so its id tells which quiz a later request means.
    _discard_attempt(record.id)
    attempt = QuizAttempt(
        user_id=record.id, started_at=started_at, quiz_state=questions, practice=practice
    )
    db.session.add(attempt)
    try:
        db.session.commit()
    except IntegrityError:
        # A simultaneous start inserted first; the unique index on user_id
        # lets only one through.
        db.session.rollback()
        return jsonify(error='Quiz already starting'), 409

    client_questions = [{'it': q['it'], 'choices': q['choices']} for q in questions]
    return jsonify(
        attempt_id=attempt.id,
        questions=client_questions,
        practice=practice,
        seconds_remaining=None if practice else _seconds_remaining(started_at),
        pauses_remaining=0 if practice else MAX_QUIZ_PAUSES,
    ), 200


@quiz_bp.route('/api/me/quiz/answer', methods=['POST'])
@require_auth
@resolve_me
def answer_quiz(record):
    body = json_body()
    index = body.get('index')
    if not isinstance(index, int) or isinstance(index, bool):
        return jsonify(error='index must be an integer'), 400

    attempt = _require_attempt(record.id, body)
    if attempt.paused_at is not None:
        return jsonify(error='Quiz is paused; call /api/me/quiz/resume first'), 409
    if not attempt.practice and _seconds_remaining(attempt.started_at) <= 0:
        return jsonify(error='Time is up; call /api/me/quiz/submit'), 409
    if attempt.next_index >= len(attempt.quiz_state):
        return jsonify(error='All questions have already been answered'), 409
    if index != attempt.next_index:
        return _out_of_sync()
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
        return _out_of_sync()

    return jsonify(correct=correct), 200


@quiz_bp.route('/api/me/quiz/pause', methods=['POST'])
@require_auth
@resolve_me
def pause_quiz(record):
    attempt = _require_attempt(record.id, json_body())
    _require_timed(attempt)
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
    attempt = _require_attempt(record.id, json_body())
    _require_timed(attempt)
    if attempt.paused_at is not None:
        # Move the start forward by the pause, so none of it counts against
        # the clock.
        attempt.started_at += utcnow() - attempt.paused_at
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
    attempt = _require_attempt(record.id, json_body())

    score = attempt.correct_count
    if attempt.practice:
        time_seconds = int((utcnow() - attempt.started_at).total_seconds())
        db.session.delete(attempt)
        db.session.commit()
        return jsonify(
            score=score, time_seconds=time_seconds, is_new_best=False, practice=True
        ), 200

    time_seconds = int(
        QUIZ_TIME_LIMIT_SECONDS - _seconds_remaining(attempt.started_at, attempt.paused_at)
    )
    db.session.delete(attempt)

    # Nothing right is never a best: an abandoned quiz would otherwise reach
    # the leaderboard as 0. One conditional update, so concurrent submits
    # can't replace a better score with a stale one.
    is_new_best = False
    if score:
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
        is_new_best = result.rowcount > 0
    db.session.commit()

    return jsonify(
        score=score, time_seconds=time_seconds, is_new_best=is_new_best, practice=False
    ), 200


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
