from datetime import UTC, datetime
from functools import wraps

from flask import g, jsonify, request
from sqlalchemy import select

from ..extensions import db
from ..models import User


def json_body():
    body = request.get_json(silent=True)
    return body if isinstance(body, dict) else None


def str_field(body, key):
    """A JSON body field as a stripped string, or '' if it's missing or not a
    string."""
    value = body.get(key)
    return value.strip() if isinstance(value, str) else ''


def find_user(sub):
    return db.session.scalars(select(User).where(User.auth0_sub == sub)).one_or_none()


def resolve_me(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        record = find_user(g.current_user_sub)
        if record is None:
            return jsonify(error='Unknown resource'), 404
        return f(record, *args, **kwargs)

    return decorated


def utcnow():
    return datetime.now(UTC)
