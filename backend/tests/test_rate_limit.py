TRANSLATE = '/api/translate'
VALID = {'text': 'ciao', 'source': 'it', 'target': 'en'}


def test_requests_past_the_limit_are_429(rate_limited_client, auth_headers, google_stub):
    headers = auth_headers(sub='auth0|ratelimit')
    google_stub.respond({'data': {'translations': [{'translatedText': 'hello'}]}})

    for _ in range(30):
        response = rate_limited_client.post(TRANSLATE, json=VALID, headers=headers)
        assert response.status_code == 200

    response = rate_limited_client.post(TRANSLATE, json=VALID, headers=headers)
    assert response.status_code == 429
