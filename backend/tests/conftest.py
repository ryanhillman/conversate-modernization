import base64
import json
import os
import time
import urllib.request

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from jose import jwt

from conversate import auth as auth_module
from conversate.app import create_app
from conversate.extensions import db
from conversate.models import User

TEST_DOMAIN = 'test-tenant.auth0.com'
TEST_AUDIENCE = 'test-audience'
ISSUER = 'https://%s/' % TEST_DOMAIN
KID = 'test-key'


class _TestConfig:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ALLOWED_ORIGIN = 'http://localhost:3000'
    AUTH0_DOMAIN = TEST_DOMAIN
    AUTH0_AUDIENCE = TEST_AUDIENCE
    GOOGLE_CLOUD_API_KEY = 'test-google-api-key'
    TESTING = True
    DEBUG = False


def _generate_pem():
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    return key, key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode()


def _b64uint(value):
    raw = value.to_bytes((value.bit_length() + 7) // 8, 'big')
    return base64.urlsafe_b64encode(raw).rstrip(b'=').decode()


@pytest.fixture(scope='session')
def signing_key():
    key, pem = _generate_pem()
    numbers = key.public_key().public_numbers()
    jwk = {
        'kty': 'RSA',
        'use': 'sig',
        'alg': 'RS256',
        'kid': KID,
        'n': _b64uint(numbers.n),
        'e': _b64uint(numbers.e),
    }
    return pem, jwk


@pytest.fixture(autouse=True)
def stub_jwks(monkeypatch, signing_key):
    _, jwk = signing_key
    monkeypatch.setattr(
        auth_module, '_get_jwks', lambda domain, force_refresh=False: {'keys': [jwk]}
    )


@pytest.fixture
def app(tmp_path):
    # SQLite does not enforce VARCHAR limits, so set TEST_DATABASE_URL to run the
    # suite against the real database engine.
    config = _TestConfig()
    config.SQLALCHEMY_DATABASE_URI = os.environ.get(
        'TEST_DATABASE_URL', 'sqlite:///%s' % (tmp_path / 'test.db').as_posix()
    )
    application = create_app(config=config)
    with application.app_context():
        db.drop_all()
        db.create_all()
        yield application
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def make_token(signing_key):
    pem, _ = signing_key

    def _make(sub='auth0|test'):
        # An Auth0 API access token identifies the user by `sub`; it does not
        # carry email.
        now = int(time.time())
        claims = {
            'sub': sub,
            'aud': TEST_AUDIENCE,
            'iss': ISSUER,
            'iat': now,
            'exp': now + 3600,
        }
        return jwt.encode(claims, pem, algorithm='RS256', headers={'kid': KID})

    return _make


@pytest.fixture
def auth_headers(make_token):
    def _headers(sub='auth0|test'):
        return {'Authorization': 'Bearer ' + make_token(sub)}

    return _headers


@pytest.fixture
def create_user(app):
    def _create(sub='auth0|test', email='user@example.com', user_name='tester',
                lessons=None):
        user = User(sub, email, user_name)
        user.lessons_completed = [] if lessons is None else lessons
        db.session.add(user)
        db.session.commit()
        return user

    return _create


class _FakeResponse:
    def __init__(self, payload):
        self._payload = json.dumps(payload).encode()

    def read(self):
        return self._payload

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


class GoogleApiStub:
    """Monkeypatches urllib.request.urlopen so tests can simulate a Google API
    response or failure without making a real network call."""

    def __init__(self, monkeypatch):
        self._response = None
        self._error = None
        monkeypatch.setattr(urllib.request, 'urlopen', self._urlopen)

    def _urlopen(self, req, timeout=None):
        if self._error is not None:
            raise self._error
        return _FakeResponse(self._response)

    def respond(self, payload):
        self._response = payload

    def fail(self, error):
        self._error = error


@pytest.fixture
def google_stub(monkeypatch):
    return GoogleApiStub(monkeypatch)
