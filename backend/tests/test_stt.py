import base64

import httpx

from conversate import google_api
from conversate.api.speech import MAX_STT_AUDIO_BYTES

STT = '/api/stt'

VALID = {'audio': 'ZmFrZS1hdWRpbw==', 'mime_type': 'audio/webm;codecs=opus', 'language': 'it'}


def test_unsupported_mime_type_is_400(client, auth_headers):
    body = dict(VALID, mime_type='audio/mp4')
    assert client.post(STT, json=body, headers=auth_headers()).status_code == 400


def test_transcribes_successfully(client, auth_headers, google_stub):
    google_stub.respond({'results': [{'alternatives': [{'transcript': 'ciao'}]}]})
    response = client.post(STT, json=VALID, headers=auth_headers())
    assert response.status_code == 200
    assert response.get_json() == {'transcript': 'ciao'}


def test_joins_the_parts_google_splits_at_pauses(client, auth_headers, google_stub):
    google_stub.respond(
        {
            'results': [
                {'alternatives': [{'transcript': 'ciao'}]},
                {'alternatives': [{'transcript': ' come stai'}]},
            ]
        }
    )
    response = client.post(STT, json=VALID, headers=auth_headers())
    assert response.get_json() == {'transcript': 'ciao come stai'}


def test_no_speech_detected_is_422(client, auth_headers, google_stub):
    google_stub.respond({'results': []})
    assert client.post(STT, json=VALID, headers=auth_headers()).status_code == 422


def test_gives_google_longer_to_transcribe(client, auth_headers, google_stub):
    google_stub.respond({'results': [{'alternatives': [{'transcript': 'ciao'}]}]})
    client.post(STT, json=VALID, headers=auth_headers())
    assert google_stub.last_call.timeout['read'] > google_api.GOOGLE_API_TIMEOUT_SECONDS


def test_upstream_failure_is_502(client, auth_headers, google_stub):
    google_stub.fail(httpx.ConnectError('boom'))
    assert client.post(STT, json=VALID, headers=auth_headers()).status_code == 502


def test_unexpected_response_shape_is_502(client, auth_headers, google_stub):
    google_stub.respond(['not', 'an', 'object'])
    assert client.post(STT, json=VALID, headers=auth_headers()).status_code == 502


def test_accepts_a_clip_of_exactly_the_size_limit(client, auth_headers, google_stub):
    google_stub.respond({'results': [{'alternatives': [{'transcript': 'ciao'}]}]})
    audio = base64.b64encode(bytes(MAX_STT_AUDIO_BYTES)).decode()
    body = dict(VALID, audio=audio)
    assert client.post(STT, json=body, headers=auth_headers()).status_code == 200
    body = dict(VALID, audio=audio + 'AAAA')
    assert client.post(STT, json=body, headers=auth_headers()).status_code == 400
