import urllib.error

TTS = '/api/tts'

VALID = {'text': 'ciao', 'language': 'it'}


def test_requires_a_token(client):
    assert client.post(TTS, json=VALID).status_code == 401


def test_requires_text(client, auth_headers):
    body = dict(VALID, text='')
    assert client.post(TTS, json=body, headers=auth_headers()).status_code == 400


def test_unsupported_language_is_400(client, auth_headers):
    body = dict(VALID, language='fr')
    assert client.post(TTS, json=body, headers=auth_headers()).status_code == 400


def test_synthesizes_successfully(client, auth_headers, google_stub):
    google_stub.respond({'audioContent': 'ZmFrZS1hdWRpbw=='})
    response = client.post(TTS, json=VALID, headers=auth_headers())
    assert response.status_code == 200
    assert response.get_json() == {'audioContent': 'ZmFrZS1hdWRpbw=='}


def test_upstream_failure_is_502(client, auth_headers, google_stub):
    google_stub.fail(urllib.error.URLError('boom'))
    assert client.post(TTS, json=VALID, headers=auth_headers()).status_code == 502
