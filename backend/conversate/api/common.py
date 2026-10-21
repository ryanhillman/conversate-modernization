from datetime import UTC, datetime
from functools import wraps

from flask import g, jsonify, request

from ..extensions import db
from ..models import User


def json_body():
    body = request.get_json(silent=True)
    return body if isinstance(body, dict) else None


def find_user(sub):
    return db.session.query(User).filter(User.auth0_sub == sub).one_or_none()


def resolve_me(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        record = find_user(g.current_user_sub)
        if record is None:
            return jsonify(error='Unknown resource'), 404
        return f(record, *args, **kwargs)

    return decorated


def utcnow():
    # Naive UTC, matching the naive DateTime column QuizAttempt.started_at is
    # stored in and compared against.
    return datetime.now(UTC).replace(tzinfo=None)
