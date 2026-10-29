import httpx

TRANSLATE = '/api/translate'

VALID = {'text': 'ciao', 'source': 'it', 'target': 'en'}


def test_requires_text(client, auth_headers):
    body = dict(VALID, text='')
    assert client.post(TRANSLATE, json=body, headers=auth_headers()).status_code == 400


def test_rejects_a_non_string_text(client, auth_headers):
    body = dict(VALID, text=5)
    assert client.post(TRANSLATE, json=body, headers=auth_headers()).status_code == 400


def test_rejects_the_same_source_and_target(client, auth_headers, google_stub):
    body = dict(VALID, target='it')
    response = client.post(TRANSLATE, json=body, headers=auth_headers())
    assert response.status_code == 400
    assert response.get_json() == {'error': 'source and target must be different'}
    assert google_stub.calls == []


def test_translates_successfully(client, auth_headers, google_stub):
    google_stub.respond({'data': {'translations': [{'translatedText': 'hello'}]}})
    response = client.post(TRANSLATE, json=VALID, headers=auth_headers())
    assert response.status_code == 200
    assert response.get_json() == {'translated_text': 'hello'}


def test_upstream_failure_is_502(client, auth_headers, google_stub):
    google_stub.fail(httpx.ConnectError('boom'))
    assert client.post(TRANSLATE, json=VALID, headers=auth_headers()).status_code == 502


def test_logs_googles_error_body_not_just_the_status(client, auth_headers, google_stub, caplog):
    google_stub.respond({'error': {'message': 'API key not valid'}}, status=403)
    response = client.post(TRANSLATE, json=VALID, headers=auth_headers())
    assert response.status_code == 502
    assert 'API key not valid' in caplog.text


def test_sends_the_api_key_header_and_the_text_to_translate(client, auth_headers, google_stub):
    google_stub.respond({'data': {'translations': [{'translatedText': 'hello'}]}})
    client.post(TRANSLATE, json=VALID, headers=auth_headers())
    call = google_stub.last_call
    assert call.headers['x-goog-api-key'] == 'test-google-api-key'
    assert call.payload['q'] == 'ciao'
