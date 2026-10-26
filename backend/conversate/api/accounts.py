import re

from flask import Blueprint, g, jsonify
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError

from ..auth import require_auth
from ..extensions import db
from ..models import QuizAttempt, User
from .common import find_user, json_body, resolve_me, str_field

accounts_bp = Blueprint('accounts_bp', __name__)

MIN_USERNAME_LENGTH = 3
MAX_USERNAME_LENGTH = 100
# Usernames appear in a URL path (the availability route), so restrict them to
# characters that are unambiguous as a path segment — no '/', space, or '?'.
_USERNAME_RE = re.compile(r'^[A-Za-z0-9_.-]+$')
# A generous sanity bound rather than the exact lesson count, so this never
# needs to track frontend/src/data/lessons.js — the frontend is the only
# client and never sends an id outside its own lesson list.
MAX_LESSON_ID = 999


def _username_error(name):
    if not name:
        return 'username is required'
    if len(name) < MIN_USERNAME_LENGTH:
        return f'username must be at least {MIN_USERNAME_LENGTH} characters'
    if len(name) > MAX_USERNAME_LENGTH:
        return f'username must be at most {MAX_USERNAME_LENGTH} characters'
    if not _USERNAME_RE.match(name):
        return 'username may only contain letters, numbers, and _ . -'
    return None


def _username_taken(name, exclude_id=None):
    query = select(User.id).where(db.func.lower(User.username) == name.lower())
    if exclude_id is not None:
        query = query.where(User.id != exclude_id)
    return db.session.scalar(query.limit(1)) is not None


def _validate_username(name, conflict_message, exclude_id=None):
    """Shared by create and rename: returns an error response, or None."""
    name_error = _username_error(name)
    if name_error:
        return jsonify(error=name_error), 400
    if _username_taken(name, exclude_id=exclude_id):
        return jsonify(error=conflict_message), 409
    return None


@accounts_bp.route('/api/me', methods=['POST'])
@require_auth
def create_me():
    sub = g.current_user_sub
    body = json_body()
    if body is None:
        return jsonify(error='Request body must be a JSON object'), 400
    username = str_field(body, 'username')
    if find_user(sub) is not None:
        return jsonify(error='User already exists'), 409
    error = _validate_username(username, 'username already exists')
    if error:
        return error
    new_user = User(sub, username)
    db.session.add(new_user)
    try:
        db.session.commit()
    except IntegrityError:
        # Both unique indexes can lose a race past the checks above: this
        # account creating twice at once, or two accounts claiming the same
        # username. Report whichever one it was.
        db.session.rollback()
        if _username_taken(username):
            return jsonify(error='username already exists'), 409
        return jsonify(error='User already exists'), 409
    return jsonify(new_user.serialize()), 201


@accounts_bp.route('/api/me', methods=['GET'])
@require_auth
@resolve_me
def get_me(record):
    return jsonify(record.serialize()), 200


@accounts_bp.route('/api/me', methods=['PUT'])
@require_auth
@resolve_me
def update_me(record):
    body = json_body()
    if body is None:
        return jsonify(error='Request body must be a JSON object'), 400
    new_name = str_field(body, 'username')
    error = _validate_username(new_name, 'username already exists', exclude_id=record.id)
    if error:
        return error
    record.username = new_name
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify(error='username already exists'), 409
    return jsonify(record.serialize()), 200


def _lock_user_for_update(sub):
    # A separate function so tests can monkeypatch it to hold the lock open
    # (sleep before returning) and force a genuine, deterministic overlap
    # with a concurrent caller, instead of hoping real threads happen to race.
    return db.session.scalars(
        select(User).where(User.auth0_sub == sub).with_for_update()
    ).one_or_none()


@accounts_bp.route('/api/me/lessons/<int:lesson_id>', methods=['POST'])
@require_auth
def complete_my_lesson(lesson_id):
    if not (1 <= lesson_id <= MAX_LESSON_ID):
        return jsonify(error='Invalid lesson id'), 400
    # lessons_completed is a JSON blob, not a set of rows, so writing it is a
    # full read-modify-write: without the lock, two concurrent completions
    # can both read the same starting list and the second commit silently
    # overwrites the first's addition. Loading the user and taking the lock
    # in one query (rather than @resolve_me plus a locking re-read) saves a
    # round trip.
    record = _lock_user_for_update(g.current_user_sub)
    if record is None:
        return jsonify(error='Unknown resource'), 404
    completed = list(record.lessons_completed or [])
    if lesson_id not in completed:
        completed.append(lesson_id)
        record.lessons_completed = completed
        db.session.commit()
    return jsonify(record.serialize()), 200


@accounts_bp.route('/api/me/reset', methods=['POST'])
@require_auth
@resolve_me
def reset_me(record):
    record.lessons_completed = []
    record.quiz_best_score = None
    record.quiz_best_time_seconds = None
    # An in-progress attempt must not survive a reset — submitting it
    # afterward would otherwise record a "new best" of whatever it had
    # scored so far (0, if nothing was answered yet).
    db.session.execute(delete(QuizAttempt).where(QuizAttempt.user_id == record.id))
    db.session.commit()
    return jsonify(record.serialize()), 200


@accounts_bp.route('/api/me', methods=['DELETE'])
@require_auth
@resolve_me
def delete_me(record):
    # Removes everything the app stores about the user. Their Auth0 login
    # identity is separate and stays; signing in again starts a new profile.
    db.session.execute(delete(QuizAttempt).where(QuizAttempt.user_id == record.id))
    db.session.delete(record)
    db.session.commit()
    return '', 204


@accounts_bp.route('/api/usernames/<username>', methods=['GET'])
@require_auth
def username_available(username):
    username = username.strip()
    name_error = _username_error(username)
    if name_error:
        return jsonify(error=name_error), 400
    return jsonify(available=not _username_taken(username)), 200
