import pytest
from sqlalchemy.exc import IntegrityError

from conversate.extensions import db
from conversate.models import User


def test_db_rejects_duplicate_sub(app):
    db.session.add(User('auth0|abc', 'alice'))
    db.session.commit()
    db.session.add(User('auth0|abc', 'bob'))
    with pytest.raises(IntegrityError):
        db.session.commit()
    db.session.rollback()


def test_db_rejects_case_variant_username(app):
    db.session.add(User('auth0|1', 'Ryan'))
    db.session.commit()
    db.session.add(User('auth0|2', 'ryan'))
    with pytest.raises(IntegrityError):
        db.session.commit()
    db.session.rollback()
