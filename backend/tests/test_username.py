URL = '/api/usernames/'


def test_requires_a_token(client):
    assert client.get(URL + 'anything').status_code == 401


def test_available_username_is_200(client, auth_headers, create_user):
    create_user(user_name='tester')
    assert client.get(URL + 'freshname', headers=auth_headers()).status_code == 200


def test_taken_username_is_409(client, auth_headers, create_user):
    create_user(user_name='tester')
    assert client.get(URL + 'tester', headers=auth_headers()).status_code == 409


def test_taken_username_is_409_any_case(client, auth_headers, create_user):
    create_user(user_name='tester')
    assert client.get(URL + 'TESTER', headers=auth_headers()).status_code == 409


def test_over_long_username_is_400(client, auth_headers):
    assert client.get(URL + 'x' * 101, headers=auth_headers()).status_code == 400


def test_invalid_characters_are_400(client, auth_headers):
    # A disallowed character that is still safe in a path segment reaches the
    # handler and is rejected by validation.
    assert client.get(URL + 'ryan!hi', headers=auth_headers()).status_code == 400
