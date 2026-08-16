import urllib.error

import pytest

TTS = '/api/tts'

VALID = {'text': 'ciao', 'language': 'it'}


def test_requires_a_token(client):
    assert client.post(TTS, json=VALID).status_code == 401


def test_requires_text(client, auth_headers):
    body = dict(VALID, text='')
    assert client.post(TTS, json=body, headers=auth_headers()).status_code == 400


def test_text_over_the_limit_is_400(client, auth_headers):
    body = dict(VALID, text='a' * 5001)
    assert client.post(TTS, json=body, headers=auth_headers()).status_code == 400


def test_limit_is_measured_in_bytes_not_characters(client, auth_headers):
    # 'à' is 2 bytes in UTF-8, so 3000 of them is 3000 characters (under a
    # character-based 5000 limit) but 6000 bytes (over the real byte limit).
    body = dict(VALID, text='à' * 3000)
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


def test_malformed_upstream_response_is_502(client, auth_headers, google_stub):
    google_stub.respond({'unexpected': 'shape'})
    assert client.post(TTS, json=VALID, headers=auth_headers()).status_code == 502


@pytest.mark.parametrize('language,language_code,voice_name', [
    ('en', 'en-US', 'en-US-Wavenet-D'),
    ('it', 'it-IT', 'it-IT-Wavenet-A'),
])
def test_sends_the_correct_outbound_request(
    client, auth_headers, google_stub, language, language_code, voice_name
):
    google_stub.respond({'audioContent': 'ZmFrZS1hdWRpbw=='})
    body = dict(VALID, language=language)
    client.post(TTS, json=body, headers=auth_headers())
    call = google_stub.last_call
    assert call.url == (
        'https://texttospeech.googleapis.com/v1/text:synthesize?key=test-google-api-key'
    )
    assert call.headers['content-type'] == 'application/json'
    assert call.timeout == 8
    assert call.payload == {
        'input': {'text': 'ciao'},
        'voice': {'languageCode': language_code, 'name': voice_name},
        'audioConfig': {'audioEncoding': 'MP3'},
    }


def test_rejected_request_makes_no_outbound_call(client, auth_headers, google_stub):
    body = dict(VALID, text='a' * 5001)
    client.post(TTS, json=body, headers=auth_headers())
    assert google_stub.calls == []
