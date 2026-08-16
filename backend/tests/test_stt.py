import urllib.error

import pytest

STT = '/api/stt'

VALID = {'audio': 'ZmFrZS1hdWRpbw==', 'mimeType': 'audio/webm;codecs=opus', 'language': 'it'}


def test_requires_a_token(client):
    assert client.post(STT, json=VALID).status_code == 401


def test_requires_audio(client, auth_headers):
    body = dict(VALID, audio='')
    assert client.post(STT, json=body, headers=auth_headers()).status_code == 400


def test_unsupported_mime_type_is_400(client, auth_headers):
    body = dict(VALID, mimeType='audio/mp4')
    assert client.post(STT, json=body, headers=auth_headers()).status_code == 400


def test_unsupported_language_is_400(client, auth_headers):
    body = dict(VALID, language='fr')
    assert client.post(STT, json=body, headers=auth_headers()).status_code == 400


def test_audio_over_the_limit_is_400(client, auth_headers):
    body = dict(VALID, audio='a' * 1_400_000)
    assert client.post(STT, json=body, headers=auth_headers()).status_code == 400


def test_transcribes_successfully(client, auth_headers, google_stub):
    google_stub.respond({'results': [{'alternatives': [{'transcript': 'ciao'}]}]})
    response = client.post(STT, json=VALID, headers=auth_headers())
    assert response.status_code == 200
    assert response.get_json() == {'transcript': 'ciao'}


def test_no_speech_detected_is_422(client, auth_headers, google_stub):
    google_stub.respond({'results': []})
    assert client.post(STT, json=VALID, headers=auth_headers()).status_code == 422


def test_upstream_failure_is_502(client, auth_headers, google_stub):
    google_stub.fail(urllib.error.URLError('boom'))
    assert client.post(STT, json=VALID, headers=auth_headers()).status_code == 502


def test_malformed_upstream_response_is_502(client, auth_headers, google_stub):
    google_stub.respond({'results': [{'unexpected': 'shape'}]})
    assert client.post(STT, json=VALID, headers=auth_headers()).status_code == 502


@pytest.mark.parametrize('language,language_code', [
    ('en', 'en-US'),
    ('it', 'it-IT'),
])
def test_sends_the_correct_outbound_request(
    client, auth_headers, google_stub, language, language_code
):
    google_stub.respond({'results': [{'alternatives': [{'transcript': 'ciao'}]}]})
    body = dict(VALID, language=language)
    client.post(STT, json=body, headers=auth_headers())
    call = google_stub.last_call
    assert call.url == (
        'https://speech.googleapis.com/v1/speech:recognize?key=test-google-api-key'
    )
    assert call.headers['content-type'] == 'application/json'
    assert call.timeout == 8
    assert call.payload == {
        'config': {'encoding': 'WEBM_OPUS', 'languageCode': language_code},
        'audio': {'content': 'ZmFrZS1hdWRpbw=='},
    }


def test_rejected_request_makes_no_outbound_call(client, auth_headers, google_stub):
    body = dict(VALID, language='fr')
    client.post(STT, json=body, headers=auth_headers())
    assert google_stub.calls == []
