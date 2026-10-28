from flask import g
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    # Names the baseline migration's foreign key; changing it would make new
    # databases differ from existing ones.
    metadata = MetaData(
        naming_convention={
            'fk': 'fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s',
        }
    )


# Keep values after commit, so a row can be serialized right after commit
# without a re-read.
db = SQLAlchemy(model_class=Base, session_options={'expire_on_commit': False})
migrate = Migrate()


def _rate_limit_key():
    # Rate-limited routes run @require_auth first, so the user's sub is set;
    # the IP is only a fallback.
    return getattr(g, 'current_user_sub', None) or get_remote_address()


limiter = Limiter(key_func=_rate_limit_key)
