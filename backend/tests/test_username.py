URL = '/api/usernames/'


def test_available_username_is_200(client, auth_headers, create_user):
    create_user(username='tester')
    response = client.get(URL + 'freshname', headers=auth_headers())
    assert response.status_code == 200
    assert response.get_json() == {'available': True}


def test_taken_username_is_200_not_available(client, auth_headers, create_user):
    create_user(username='tester')
    response = client.get(URL + 'tester', headers=auth_headers())
    assert response.status_code == 200
    assert response.get_json() == {'available': False}
