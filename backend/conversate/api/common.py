from datetime import UTC, datetime
from functools import wraps

from flask import abort, g, jsonify, request
from sqlalchemy import select

from ..extensions import db
from ..models import User


def json_body():
    """The request's JSON object; anything else is rejected with a 400."""
    try:
        body = request.get_json(silent=True)
    except RecursionError:
        # Nested too deeply for the JSON parser, which silent=True doesn't cover.
        body = None
    if not isinstance(body, dict):
        abort(400, description='Request body must be a JSON object')
    return body


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
            return jsonify(error='Profile not found'), 404
        return f(record, *args, **kwargs)

    return decorated


def utcnow():
    return datetime.now(UTC)
