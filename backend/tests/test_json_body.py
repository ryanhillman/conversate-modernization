import pytest

ROUTES = [
    ('post', '/api/me'),
    ('put', '/api/me'),
    ('post', '/api/me/quiz/answer'),
    ('post', '/api/me/quiz/pause'),
    ('post', '/api/me/quiz/resume'),
    ('post', '/api/me/quiz/submit'),
    ('post', '/api/translate'),
    ('post', '/api/tts'),
    ('post', '/api/stt'),
]
BODIES = [{'json': []}, {'data': 'not json', 'content_type': 'text/plain'}]


@pytest.mark.parametrize(('method', 'url'), ROUTES)
@pytest.mark.parametrize('body', BODIES)
def test_a_body_that_isnt_a_json_object_is_400(
    client, auth_headers, create_user, method, url, body
):
    create_user()
    response = getattr(client, method)(url, headers=auth_headers(), **body)
    assert response.status_code == 400
    assert response.get_json() == {'error': 'Request body must be a JSON object'}


def test_deeply_nested_json_is_400_not_a_server_error(client, auth_headers, create_user):
    create_user()
    body = '[' * 100_000 + ']' * 100_000
    response = client.put(
        '/api/me', data=body, content_type='application/json', headers=auth_headers()
    )
    assert response.status_code == 400
    assert response.get_json() == {'error': 'Request body must be a JSON object'}
