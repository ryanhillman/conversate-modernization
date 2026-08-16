ME = '/api/me'

VALID = {'user_name': 'tester', 'email': 'real@example.com'}


def test_requires_a_token(client):
    assert client.get(ME).status_code == 401
    assert client.post(ME, json=VALID).status_code == 401
    assert client.post(ME + '/reset').status_code == 401
    assert client.post(ME + '/lessons/1').status_code == 401


def test_token_without_sub_claim_is_401(client, make_token):
    token = make_token(sub='')
    assert client.get(ME, headers={'Authorization': 'Bearer ' + token}).status_code == 401


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


def test_create_rejects_a_short_username(client, auth_headers):
    response = client.post(ME, json={'user_name': 'ab', 'email': 'a@b.com'},
                           headers=auth_headers())
    assert response.status_code == 400
    assert 'user_name' in response.get_json()['error']


def test_a_username_at_the_limit_is_accepted(client, auth_headers):
    response = client.post(ME, json={'user_name': 'x' * 100, 'email': 'a@b.com'},
                           headers=auth_headers())
    assert response.status_code == 201


def test_create_rejects_a_non_json_body(client, auth_headers):
    headers = auth_headers()
    headers['Content-Type'] = 'application/json'
    assert client.post(ME, data='not json', headers=headers).status_code == 400


def test_create_rejects_a_duplicate(client, auth_headers, create_user):
    create_user(sub='auth0|test', user_name='tester')
    response = client.post(ME, json={'user_name': 'other', 'email': 'a@b.com'},
                           headers=auth_headers(sub='auth0|test'))
    assert response.status_code == 409


def test_create_rejects_taken_username(client, auth_headers, create_user):
    create_user(sub='auth0|owner', user_name='tester')
    response = client.post(ME, json={'user_name': 'TESTER', 'email': 'a@b.com'},
                           headers=auth_headers(sub='auth0|newcomer'))
    assert response.status_code == 409


def test_get_without_profile_is_404(client, auth_headers):
    assert client.get(ME, headers=auth_headers()).status_code == 404


def test_resolution_is_by_sub_not_email(client, auth_headers, create_user):
    # Email is profile data, not identity: the same subject always resolves the
    # same account, and a shared email does not merge accounts.
    create_user(sub='auth0|stable', email='shared@example.com', user_name='first')
    create_user(sub='auth0|other', email='shared@example.com', user_name='second')
    body = client.get(ME, headers=auth_headers(sub='auth0|stable')).get_json()
    assert body['user_name'] == 'first'


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


def test_rename_to_your_own_username_is_allowed(client, auth_headers, create_user):
    create_user(user_name='tester')
    assert client.put(ME, json={'user_name': 'tester'}, headers=auth_headers()).status_code == 200


def test_rename_rejects_a_short_username(client, auth_headers, create_user):
    create_user()
    assert client.put(ME, json={'user_name': 'ab'}, headers=auth_headers()).status_code == 400


def test_completing_a_lesson_records_it_and_scores_it(client, auth_headers, create_user):
    create_user()
    body = client.post(ME + '/lessons/1', headers=auth_headers()).get_json()
    assert body['lessons_completed'] == [1]
    assert body['score'] == 1


def test_completing_a_lesson_twice_does_not_double_count(client, auth_headers, create_user):
    create_user()
    client.post(ME + '/lessons/1', headers=auth_headers())
    body = client.post(ME + '/lessons/1', headers=auth_headers()).get_json()
    assert body['lessons_completed'] == [1]
    assert body['score'] == 1


def test_lesson_id_out_of_range_is_400(client, auth_headers, create_user):
    create_user()
    assert client.post(ME + '/lessons/0', headers=auth_headers()).status_code == 400
    assert client.post(ME + '/lessons/11', headers=auth_headers()).status_code == 400


def test_reset_clears_score_and_lessons(client, auth_headers, create_user):
    create_user(lessons=[1, 2, 3])
    body = client.post(ME + '/reset', headers=auth_headers()).get_json()
    assert body['score'] == 0
    assert body['lessons_completed'] == []


def test_reset_only_touches_your_own_record(client, auth_headers, create_user):
    create_user(sub='auth0|mine', user_name='mine', lessons=[1, 2])
    create_user(sub='auth0|theirs', user_name='theirs', lessons=[3, 4])
    client.post(ME + '/reset', headers=auth_headers(sub='auth0|mine'))
    victim = client.get(ME, headers=auth_headers(sub='auth0|theirs')).get_json()
    assert victim['score'] == 2
    assert victim['lessons_completed'] == [3, 4]


def test_reset_without_profile_is_404(client, auth_headers):
    assert client.post(ME + '/reset', headers=auth_headers()).status_code == 404
