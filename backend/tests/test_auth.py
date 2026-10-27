import logging
from urllib.error import URLError

import pytest

from conversate import auth as auth_module

URL = '/api/me'


def test_health_needs_no_token(client):
    assert client.get('/health').status_code == 200


def test_missing_authorization_header_is_401(client):
    assert client.get(URL).status_code == 401


def test_malformed_token_is_401(client):
    headers = {'Authorization': 'Bearer not.a.real.token'}
    assert client.get(URL, headers=headers).status_code == 401


def test_wrong_audience_is_401_and_logged(client, auth_headers, caplog):
    headers = auth_headers(audience='another-api')
    with caplog.at_level(logging.INFO):
        assert client.get(URL, headers=headers).status_code == 401
    assert "Rejected token: Audience doesn't match" in caplog.text


def test_a_bug_in_token_checking_is_not_reported_as_401(client, auth_headers, monkeypatch):
    def broken():
        raise RuntimeError('bug')

    monkeypatch.setattr(auth_module, '_verify_token', broken)
    with pytest.raises(RuntimeError):
        client.get(URL, headers=auth_headers())


def test_wrong_issuer_is_401(client, auth_headers):
    headers = auth_headers(issuer='https://evil.example.com/')
    assert client.get(URL, headers=headers).status_code == 401


def test_small_clock_skew_in_the_future_is_still_accepted(client, auth_headers, create_user):
    create_user()
    headers = auth_headers(iat_offset=30)
    assert client.get(URL, headers=headers).status_code == 200


def test_large_clock_skew_in_the_future_is_401(client, auth_headers):
    headers = auth_headers(iat_offset=300)
    assert client.get(URL, headers=headers).status_code == 401


def test_jwks_unreachable_is_503_not_401_after_retrying(client, auth_headers, stub_jwks):
    stub_jwks.error = URLError('connection refused')
    assert client.get(URL, headers=auth_headers()).status_code == 503
    assert stub_jwks.fetches == 4
    assert stub_jwks.sleeps == [0.5, 1, 2]


def test_a_failed_key_download_is_retried(client, auth_headers, create_user, stub_jwks):
    create_user()
    stub_jwks.error = URLError(ConnectionResetError(10054, 'connection forcibly closed'))
    stub_jwks.failures = 2
    assert client.get(URL, headers=auth_headers()).status_code == 200
    assert stub_jwks.fetches == 3
    assert stub_jwks.sleeps == [0.5, 1]


def test_a_key_download_timeout_isnt_retried(client, auth_headers, stub_jwks):
    stub_jwks.error = URLError(TimeoutError('timed out'))
    assert client.get(URL, headers=auth_headers()).status_code == 503
    assert stub_jwks.fetches == 1
    assert stub_jwks.sleeps == []


def test_unknown_key_ids_dont_refetch_keys_during_the_cooldown(client, auth_headers, stub_jwks):
    for _ in range(3):
        headers = auth_headers(kid='forged-key')
        assert client.get(URL, headers=headers).status_code == 401
    assert stub_jwks.fetches == 1
