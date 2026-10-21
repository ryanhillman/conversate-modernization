import urllib.error

TRANSLATE = '/api/translate'

VALID = {'text': 'ciao', 'source': 'it', 'target': 'en'}


def test_requires_a_token(client):
    assert client.post(TRANSLATE, json=VALID).status_code == 401


def test_requires_text(client, auth_headers):
    body = dict(VALID, text='')
    assert client.post(TRANSLATE, json=body, headers=auth_headers()).status_code == 400


def test_translates_successfully(client, auth_headers, google_stub):
    google_stub.respond({'data': {'translations': [{'translatedText': 'hello'}]}})
    response = client.post(TRANSLATE, json=VALID, headers=auth_headers())
    assert response.status_code == 200
    assert response.get_json() == {'translatedText': 'hello'}


def test_upstream_failure_is_502(client, auth_headers, google_stub):
    google_stub.fail(urllib.error.URLError('boom'))
    assert client.post(TRANSLATE, json=VALID, headers=auth_headers()).status_code == 502


def test_sends_the_api_key_header_and_the_text_to_translate(client, auth_headers, google_stub):
    google_stub.respond({'data': {'translations': [{'translatedText': 'hello'}]}})
    client.post(TRANSLATE, json=VALID, headers=auth_headers())
    call = google_stub.last_call
    assert call.headers['x-goog-api-key'] == 'test-google-api-key'
    assert call.payload['q'] == 'ciao'
