from flask import g
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData

# Changing this convention rewrites the DDL that the existing baseline migration
# emits, so a fresh database would diverge from an existing one.
metadata = MetaData(
    naming_convention={
        'fk': 'fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s',
    }
)

db = SQLAlchemy(metadata=metadata)
migrate = Migrate()


def _rate_limit_key():
    # Routes that rate-limit run @require_auth first, so the authenticated
    # user's sub is already set; fall back to the IP only for safety.
    return getattr(g, 'current_user_sub', None) or get_remote_address()


limiter = Limiter(key_func=_rate_limit_key)
