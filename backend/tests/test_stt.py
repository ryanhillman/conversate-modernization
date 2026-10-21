import urllib.error

STT = '/api/stt'

VALID = {'audio': 'ZmFrZS1hdWRpbw==', 'mimeType': 'audio/webm;codecs=opus', 'language': 'it'}


def test_requires_a_token(client):
    assert client.post(STT, json=VALID).status_code == 401


def test_unsupported_mime_type_is_400(client, auth_headers):
    body = dict(VALID, mimeType='audio/mp4')
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
