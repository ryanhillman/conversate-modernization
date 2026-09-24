from datetime import datetime, timezone
from functools import wraps

from flask import request, jsonify, g

from ..extensions import db
from ..models import User


def _json_body():
    body = request.get_json(silent=True)
    return body if isinstance(body, dict) else None


def _find_user(sub):
    return db.session.query(User).filter(User.auth0_sub == sub).one_or_none()


def _resolve_me(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        record = _find_user(g.current_user_sub)
        if record is None:
            return jsonify(error='Unknown resource'), 404
        return f(record, *args, **kwargs)
    return decorated


def _utcnow():
    # Naive UTC, matching the naive DateTime column quiz_state.started_at is
    # stored in and compared against.
    return datetime.now(timezone.utc).replace(tzinfo=None)
