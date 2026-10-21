from conversate import auth as auth_module
from conversate.auth import JwksUnavailable

URL = '/api/me'


def test_health_needs_no_token(client):
    assert client.get('/health').status_code == 200


def test_missing_authorization_header_is_401(client):
    assert client.get(URL).status_code == 401


def test_malformed_token_is_401(client):
    headers = {'Authorization': 'Bearer not.a.real.token'}
    assert client.get(URL, headers=headers).status_code == 401


def test_wrong_audience_is_401(client, auth_headers):
    headers = auth_headers(audience='another-api')
    assert client.get(URL, headers=headers).status_code == 401


def test_wrong_issuer_is_401(client, auth_headers):
    headers = auth_headers(issuer='https://evil.example.com/')
    assert client.get(URL, headers=headers).status_code == 401


def test_jwks_unreachable_is_503_not_401(client, auth_headers, monkeypatch):
    headers = auth_headers()

    def unreachable(domain, force_refresh=False):
        raise JwksUnavailable('connection refused')

    monkeypatch.setattr(auth_module, '_get_jwks', unreachable)
    assert client.get(URL, headers=headers).status_code == 503
