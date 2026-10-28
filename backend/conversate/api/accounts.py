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
# Usernames go in a URL path (/api/usernames/<name>), so allow only path-safe
# characters.
_USERNAME_RE = re.compile(r'^[A-Za-z0-9_.-]+$')
# A sanity bound, not the lesson count, so it needn't track the frontend's
# lessons.js.
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


def _username_taken_response():
    # The frontend checks the code, so the wording can change freely.
    return jsonify(error='username already exists', code='username_taken'), 409


def _validate_username(name, exclude_id=None):
    """Shared by create and rename: returns an error response, or None."""
    name_error = _username_error(name)
    if name_error:
        return jsonify(error=name_error), 400
    if _username_taken(name, exclude_id=exclude_id):
        return _username_taken_response()
    return None


@accounts_bp.route('/api/me', methods=['POST'])
@require_auth
def create_me():
    sub = g.current_user_sub
    body = json_body()
    username = str_field(body, 'username')
    if find_user(sub) is not None:
        return jsonify(error='Profile already exists'), 409
    error = _validate_username(username)
    if error:
        return error
    new_user = User(sub, username)
    db.session.add(new_user)
    try:
        db.session.commit()
    except IntegrityError:
        # Either unique index can lose a race past the checks above: this
        # account creating twice, or another account taking the name.
        db.session.rollback()
        if _username_taken(username):
            return _username_taken_response()
        return jsonify(error='Profile already exists'), 409
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
    new_name = str_field(body, 'username')
    error = _validate_username(new_name, exclude_id=record.id)
    if error:
        return error
    record.username = new_name
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return _username_taken_response()
    return jsonify(record.serialize()), 200


def _lock_user_for_update(sub):
    # Separate so tests can hold the lock open and force a real overlap.
    return db.session.scalars(
        select(User).where(User.auth0_sub == sub).with_for_update()
    ).one_or_none()


@accounts_bp.route('/api/me/lessons/<int:lesson_id>', methods=['POST'])
@require_auth
def complete_my_lesson(lesson_id):
    if not (1 <= lesson_id <= MAX_LESSON_ID):
        return jsonify(error='Invalid lesson id'), 400
    # lessons_completed is a JSON list, so adding to it is a read-modify-write.
    # Lock the row so concurrent completions can't overwrite each other.
    record = _lock_user_for_update(g.current_user_sub)
    if record is None:
        return jsonify(error='Profile not found'), 404
    completed = list(record.lessons_completed)
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
    # A leftover attempt could otherwise be submitted as a new best.
    db.session.execute(delete(QuizAttempt).where(QuizAttempt.user_id == record.id))
    db.session.commit()
    return jsonify(record.serialize()), 200


@accounts_bp.route('/api/me', methods=['DELETE'])
@require_auth
@resolve_me
def delete_me(record):
    # The Auth0 login stays; signing in again starts a new profile.
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
