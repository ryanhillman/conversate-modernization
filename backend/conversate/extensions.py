from flask import g
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    # Names the foreign key the baseline migration creates. Changing it would
    # give a fresh database a different constraint name than an existing one.
    metadata = MetaData(
        naming_convention={
            'fk': 'fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s',
        }
    )


# Each request gets its own short-lived session, so keeping values loaded after
# commit can't serve stale data, and serializing a just-saved row needs no
# re-read.
db = SQLAlchemy(model_class=Base, session_options={'expire_on_commit': False})
migrate = Migrate()


def _rate_limit_key():
    # Routes that rate-limit run @require_auth first, so the authenticated
    # user's sub is already set; fall back to the IP only for safety.
    return getattr(g, 'current_user_sub', None) or get_remote_address()


limiter = Limiter(key_func=_rate_limit_key)
