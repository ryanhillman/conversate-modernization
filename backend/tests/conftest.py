import base64
import io
import json
import os
import time
import urllib.request

import httpx
import jwt
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from conversate import auth as auth_module
from conversate import google_api
from conversate.app import create_app
from conversate.extensions import db
from conversate.models import User

TEST_DOMAIN = 'test-tenant.auth0.com'
TEST_AUDIENCE = 'test-audience'
ISSUER = f'https://{TEST_DOMAIN}/'
KID = 'test-key'

# The app fixture below calls db.drop_all()/create_all() around every test.
# Pointed at the app's own database by mistake, that wipes its data — refuse
# to run rather than risk it.
_test_db_url = os.environ.get('TEST_DATABASE_URL')
if _test_db_url and not _test_db_url.rsplit('/', 1)[-1].endswith('_test'):
    pytest.exit('TEST_DATABASE_URL must point at a database whose name ends in _test')


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


class JwksStub:
    """Stands in for the HTTP opener PyJWKClient fetches Auth0's keys with,
    so the client's own caching and cooldown still run. Serves the test
    signing key and counts the fetches, or fails them like an unreachable
    Auth0."""

    def __init__(self, jwk):
        self.jwk = jwk
        self.fetches = 0
        self.error = None

    def open(self, request, timeout=None):
        self.fetches += 1
        if self.error is not None:
            raise self.error
        return io.BytesIO(json.dumps({'keys': [self.jwk]}).encode())


@pytest.fixture(autouse=True)
def stub_jwks(monkeypatch, signing_key):
    _, jwk = signing_key
    stub = JwksStub(jwk)
    # Fresh clients per test, so no test sees keys another one cached.
    monkeypatch.setattr(auth_module, '_jwks_clients', {})
    monkeypatch.setattr(urllib.request, 'build_opener', lambda *handlers: stub)
    return stub


@pytest.fixture
def app(tmp_path):
    # SQLite does not enforce VARCHAR limits, so set TEST_DATABASE_URL to run the
    # suite against the real database engine.
    config = _TestConfig()
    config.SQLALCHEMY_DATABASE_URI = os.environ.get(
        'TEST_DATABASE_URL', f'sqlite:///{(tmp_path / "test.db").as_posix()}'
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

    def _make(sub='auth0|test', audience=TEST_AUDIENCE, issuer=ISSUER, iat_offset=0, kid=KID):
        # An Auth0 API access token identifies the user by `sub`; it does not
        # carry email.
        now = int(time.time()) + iat_offset
        claims = {
            'sub': sub,
            'aud': audience,
            'iss': issuer,
            'iat': now,
            'exp': now + 3600,
        }
        return jwt.encode(claims, pem, algorithm='RS256', headers={'kid': kid})

    return _make


@pytest.fixture
def auth_headers(make_token):
    def _headers(sub='auth0|test', **kwargs):
        return {'Authorization': 'Bearer ' + make_token(sub, **kwargs)}

    return _headers


@pytest.fixture
def create_user(app):
    def _create(sub='auth0|test', username='tester', lessons=None):
        user = User(sub, username)
        user.lessons_completed = [] if lessons is None else lessons
        db.session.add(user)
        db.session.commit()
        return user

    return _create


class _RecordedCall:
    def __init__(self, request):
        self.url = str(request.url)
        self.payload = json.loads(request.content)
        self.headers = dict(request.headers)  # httpx lowercases header names
        self.timeout = request.extensions.get('timeout')


class GoogleApiStub:
    """Swaps google_api's shared HTTP client for one backed by a mock
    transport and records every outbound call, so tests can simulate a
    Google API response/failure and assert on what the app actually sent
    (the key header, the request body)."""

    def __init__(self, monkeypatch):
        self.calls = []
        self._response = None
        self._status = 200
        self._error = None
        client = httpx.Client(
            transport=httpx.MockTransport(self._handle),
            timeout=google_api.GOOGLE_API_TIMEOUT_SECONDS,
        )
        monkeypatch.setattr(google_api, '_client', client)

    def _handle(self, request):
        self.calls.append(_RecordedCall(request))
        if self._error is not None:
            raise self._error
        return httpx.Response(self._status, json=self._response)

    def respond(self, payload, status=200):
        self._response = payload
        self._status = status

    def fail(self, error):
        self._error = error

    @property
    def last_call(self):
        return self.calls[-1]


@pytest.fixture
def google_stub(monkeypatch):
    return GoogleApiStub(monkeypatch)


@pytest.fixture
def rate_limited_client(tmp_path):
    # A dedicated app/client (own db, own user) with rate limiting left on,
    # for the one test that needs it; the standard `app`/`client` fixtures
    # disable it so the rest of the suite isn't order-dependent on shared
    # hit counts. Separate from `create_user`, which is wired to `app`.
    config = _TestConfig()
    config.RATELIMIT_ENABLED = True
    config.SQLALCHEMY_DATABASE_URI = os.environ.get(
        'TEST_DATABASE_URL', f'sqlite:///{(tmp_path / "ratelimit.db").as_posix()}'
    )
    application = create_app(config=config)
    with application.app_context():
        db.drop_all()
        db.create_all()
        db.session.add(User('auth0|ratelimit', 'ratelimited'))
        db.session.commit()
        yield application.test_client()
        db.session.remove()
        db.drop_all()
