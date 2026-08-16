import pytest
from sqlalchemy.exc import IntegrityError

from conversate.extensions import db
from conversate.models import User


def test_db_rejects_duplicate_sub(app):
    db.session.add(User('auth0|abc', 'a@example.com', 'alice'))
    db.session.commit()
    db.session.add(User('auth0|abc', 'b@example.com', 'bob'))
    with pytest.raises(IntegrityError):
        db.session.commit()
    db.session.rollback()


def test_db_rejects_case_variant_username(app):
    db.session.add(User('auth0|1', 'ryan@example.com', 'Ryan'))
    db.session.commit()
    db.session.add(User('auth0|2', 'other@example.com', 'ryan'))
    with pytest.raises(IntegrityError):
        db.session.commit()
    db.session.rollback()


def test_db_allows_duplicate_email(app):
    # Email is profile data, not identity, so two subjects may share one.
    db.session.add(User('auth0|1', 'shared@example.com', 'alice'))
    db.session.add(User('auth0|2', 'shared@example.com', 'bob'))
    db.session.commit()
    assert db.session.query(User).count() == 2
