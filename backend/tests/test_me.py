ME = '/api/me'

VALID = {'user_name': 'tester', 'email': 'real@example.com'}


def test_requires_a_token(client):
    assert client.get(ME).status_code == 401
    assert client.post(ME, json=VALID).status_code == 401
    assert client.post(ME + '/reset').status_code == 401
    assert client.post(ME + '/lessons/1').status_code == 401


def test_create_stores_body_email(client, auth_headers):
    response = client.post(ME, json={
        'user_name': 'tester',
        'email': 'real@example.com',
    }, headers=auth_headers())
    assert response.status_code == 201
    assert response.get_json()['email'] == 'real@example.com'


def test_create_requires_a_valid_email(client, auth_headers):
    assert client.post(ME, json={'user_name': 'tester'}, headers=auth_headers()).status_code == 400
    assert client.post(ME, json={'user_name': 'tester', 'email': 'notanemail'},
                       headers=auth_headers()).status_code == 400


def test_create_rejects_a_duplicate(client, auth_headers, create_user):
    create_user(sub='auth0|test', user_name='tester')
    response = client.post(ME, json={'user_name': 'other', 'email': 'a@b.com'},
                           headers=auth_headers(sub='auth0|test'))
    assert response.status_code == 409


def test_get_without_profile_is_404(client, auth_headers):
    assert client.get(ME, headers=auth_headers()).status_code == 404


def test_rename(client, auth_headers, create_user):
    create_user()
    response = client.put(ME, json={'user_name': 'renamed'}, headers=auth_headers())
    assert response.status_code == 200
    assert response.get_json()['user_name'] == 'renamed'


def test_rename_to_a_taken_username_is_409(client, auth_headers, create_user):
    create_user(sub='auth0|me', user_name='tester')
    create_user(sub='auth0|other', user_name='taken')
    assert client.put(ME, json={'user_name': 'taken'},
                      headers=auth_headers(sub='auth0|me')).status_code == 409


def test_completing_a_lesson_twice_does_not_double_count(client, auth_headers, create_user):
    create_user()
    client.post(ME + '/lessons/1', headers=auth_headers())
    body = client.post(ME + '/lessons/1', headers=auth_headers()).get_json()
    assert body['lessons_completed'] == [1]
    assert body['score'] == 1


def test_reset_clears_score_and_lessons(client, auth_headers, create_user):
    create_user(lessons=[1, 2, 3])
    body = client.post(ME + '/reset', headers=auth_headers()).get_json()
    assert body['score'] == 0
    assert body['lessons_completed'] == []
