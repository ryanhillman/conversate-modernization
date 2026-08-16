import urllib.error

TRANSLATE = '/api/translate'

VALID = {'text': 'ciao', 'source': 'it', 'target': 'en'}


def test_requires_a_token(client):
    assert client.post(TRANSLATE, json=VALID).status_code == 401


def test_requires_text(client, auth_headers):
    body = dict(VALID, text='')
    assert client.post(TRANSLATE, json=body, headers=auth_headers()).status_code == 400


def test_text_over_the_limit_is_400(client, auth_headers):
    body = dict(VALID, text='a' * 5001)
    assert client.post(TRANSLATE, json=body, headers=auth_headers()).status_code == 400


def test_unsupported_language_is_400(client, auth_headers):
    body = dict(VALID, target='fr')
    assert client.post(TRANSLATE, json=body, headers=auth_headers()).status_code == 400


def test_translates_successfully(client, auth_headers, google_stub):
    google_stub.respond({'data': {'translations': [{'translatedText': 'hello'}]}})
    response = client.post(TRANSLATE, json=VALID, headers=auth_headers())
    assert response.status_code == 200
    assert response.get_json() == {'translatedText': 'hello'}


def test_upstream_failure_is_502(client, auth_headers, google_stub):
    google_stub.fail(urllib.error.URLError('boom'))
    assert client.post(TRANSLATE, json=VALID, headers=auth_headers()).status_code == 502


def test_malformed_upstream_response_is_502(client, auth_headers, google_stub):
    google_stub.respond({'unexpected': 'shape'})
    assert client.post(TRANSLATE, json=VALID, headers=auth_headers()).status_code == 502


def test_sends_the_correct_outbound_request(client, auth_headers, google_stub):
    google_stub.respond({'data': {'translations': [{'translatedText': 'hello'}]}})
    client.post(TRANSLATE, json=VALID, headers=auth_headers())
    call = google_stub.last_call
    assert call.url == (
        'https://translation.googleapis.com/language/translate/v2?key=test-google-api-key'
    )
    assert call.headers['content-type'] == 'application/json'
    assert call.timeout == 8
    assert call.payload == {
        'q': 'ciao',
        'source': 'it',
        'target': 'en',
        'format': 'text',
    }


def test_rejected_request_makes_no_outbound_call(client, auth_headers, google_stub):
    body = dict(VALID, target='fr')
    client.post(TRANSLATE, json=body, headers=auth_headers())
    assert google_stub.calls == []
