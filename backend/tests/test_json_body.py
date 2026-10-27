import pytest

ROUTES = [
    ('post', '/api/me'),
    ('put', '/api/me'),
    ('post', '/api/me/quiz/answer'),
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
