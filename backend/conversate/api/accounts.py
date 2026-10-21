import re

from flask import Blueprint, jsonify, g
from sqlalchemy.exc import IntegrityError

from ..extensions import db
from ..models import User
from ..auth import require_auth
from .common import _json_body, _find_user, _resolve_me

accounts_bp = Blueprint('accounts_bp', __name__)

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


_EMAIL_INVALID = object()


def _body_email(body):
    """None if the client didn't supply one (email is optional — some Auth0
    connections never return one). _EMAIL_INVALID if one was supplied but
    doesn't look like an address."""
    email = (body.get('email') or '').strip()
    if not email:
        return None
    if not _EMAIL_RE.match(email) or len(email) > MAX_EMAIL_LENGTH:
        return _EMAIL_INVALID
    return email


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


@accounts_bp.route('/api/me', methods=['POST'])
@require_auth
def create_me():
    sub = g.current_user_sub
    body = _json_body()
    if body is None:
        return jsonify(error='Request body must be a JSON object'), 400
    user_name = (body.get('user_name') or '').strip()
    email = _body_email(body)
    if email is _EMAIL_INVALID:
        return jsonify(error='email must be a valid address'), 400
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


@accounts_bp.route('/api/me', methods=['GET'])
@require_auth
@_resolve_me
def get_me(record):
    return jsonify(record.serialize()), 200


@accounts_bp.route('/api/me', methods=['PUT'])
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


@accounts_bp.route('/api/me/lessons/<int:lesson_id>', methods=['POST'])
@require_auth
@_resolve_me
def complete_my_lesson(record, lesson_id):
    if lesson_id not in VALID_LESSON_IDS:
        return jsonify(error='Invalid lesson id'), 400
    # lessons_completed is a JSON blob, not a set of rows, so writing it is a
    # full read-modify-write: without the lock, two concurrent completions
    # can both read the same starting list and the second commit silently
    # overwrites the first's addition.
    record = (
        db.session.query(User).filter(User.id == record.id)
        .populate_existing().with_for_update().one()
    )
    completed = list(record.lessons_completed or [])
    if lesson_id not in completed:
        completed.append(lesson_id)
        record.lessons_completed = completed
        db.session.commit()
    return jsonify(record.serialize()), 200


@accounts_bp.route('/api/me/reset', methods=['POST'])
@require_auth
@_resolve_me
def reset_me(record):
    record.lessons_completed = []
    record.quiz_best_score = None
    record.quiz_best_time_seconds = None
    db.session.commit()
    return jsonify(record.serialize()), 200


@accounts_bp.route('/api/usernames/<user_name>', methods=['GET'])
@require_auth
def username_available(user_name):
    user_name = user_name.strip()
    name_error = _username_error(user_name)
    if name_error:
        return jsonify(error=name_error), 400
    if _username_taken(user_name):
        return jsonify(error='user_name already exists'), 409
    return jsonify(message='Success'), 200
