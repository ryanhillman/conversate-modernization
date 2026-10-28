import pytest

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


@pytest.mark.parametrize(
    ('name', 'error'),
    [
        ('ab', 'username must be at least 3 characters'),
        ('a' * 101, 'username must be at most 100 characters'),
        ('bad!name', 'username may only contain letters, numbers, and _ . -'),
    ],
)
def test_a_username_breaking_the_format_rules_is_400(client, auth_headers, name, error):
    response = client.get(URL + name, headers=auth_headers())
    assert response.status_code == 400
    assert response.get_json() == {'error': error}
