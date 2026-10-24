import re

from flask import Blueprint, g, jsonify
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
        return 'user_name is required'
    if len(name) < MIN_USERNAME_LENGTH:
        return f'user_name must be at least {MIN_USERNAME_LENGTH} characters'
    if len(name) > MAX_USERNAME_LENGTH:
        return f'user_name must be at most {MAX_USERNAME_LENGTH} characters'
    if not _USERNAME_RE.match(name):
        return 'user_name may only contain letters, numbers, and _ . -'
    return None


def _username_taken(name, exclude_id=None):
    query = db.session.query(User.id).filter(db.func.lower(User.user_name) == name.lower())
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


@accounts_bp.route('/api/me', methods=['POST'])
@require_auth
def create_me():
    sub = g.current_user_sub
    body = json_body()
    if body is None:
        return jsonify(error='Request body must be a JSON object'), 400
    user_name = str_field(body, 'user_name')
    if find_user(sub) is not None:
        return jsonify(error='User already exists'), 409
    error = _validate_username(user_name, 'user_name already exists')
    if error:
        return error
    new_user = User(sub, user_name)
    db.session.add(new_user)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
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
    new_name = str_field(body, 'user_name')
    error = _validate_username(new_name, 'user_name already exists', exclude_id=record.id)
    if error:
        return error
    record.user_name = new_name
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify(error='user_name already exists'), 409
    return jsonify(record.serialize()), 200


def _lock_user_for_update(sub):
    # A separate function so tests can monkeypatch it to hold the lock open
    # (sleep before returning) and force a genuine, deterministic overlap
    # with a concurrent caller, instead of hoping real threads happen to race.
    return db.session.query(User).filter(User.auth0_sub == sub).with_for_update().one_or_none()


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
    db.session.query(QuizAttempt).filter(QuizAttempt.user_id == record.id).delete()
    db.session.commit()
    return jsonify(record.serialize()), 200


@accounts_bp.route('/api/usernames/<user_name>', methods=['GET'])
@require_auth
def username_available(user_name):
    user_name = user_name.strip()
    name_error = _username_error(user_name)
    if name_error:
        return jsonify(error=name_error), 400
    return jsonify(available=not _username_taken(user_name)), 200
