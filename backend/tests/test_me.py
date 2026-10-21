import os
import threading

import pytest

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


def test_get_resolves_to_the_authenticated_user_not_just_any_user(client, auth_headers, create_user):
    create_user(sub='auth0|a', user_name='alice')
    create_user(sub='auth0|b', user_name='bob')
    body = client.get(ME, headers=auth_headers(sub='auth0|b')).get_json()
    assert body['user_name'] == 'bob'


def test_reset_does_not_touch_another_users_record(client, auth_headers, create_user):
    create_user(sub='auth0|a', user_name='alice', lessons=[1, 2])
    create_user(sub='auth0|b', user_name='bob', lessons=[3, 4])
    client.post(ME + '/reset', headers=auth_headers(sub='auth0|b'))
    untouched = client.get(ME, headers=auth_headers(sub='auth0|a')).get_json()
    assert untouched['lessons_completed'] == [1, 2]


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


@pytest.mark.skipif(
    not os.environ.get('TEST_DATABASE_URL'),
    reason="SQLite silently ignores SELECT ... FOR UPDATE (no FOR UPDATE clause "
           "is even generated), so the lock this test depends on has no effect "
           "there. Run with TEST_DATABASE_URL pointing at Postgres to exercise it.",
)
def test_concurrent_lesson_completions_do_not_lose_one(app, client, auth_headers, create_user):
    # lessons_completed is a JSON blob, so completing two different lessons
    # "at once" is a read-modify-write race: without a lock, both requests
    # can read the same starting list and the second commit overwrites the
    # first's addition. The row lock makes the outcome correct regardless of
    # how the two requests actually interleave, so real threads (unlike the
    # quiz-start race) give a reliable test here.
    user = create_user()
    headers = auth_headers()
    barrier = threading.Barrier(2)

    def complete(lesson_id):
        barrier.wait()
        client.post(ME + '/lessons/%d' % lesson_id, headers=headers)

    threads = [threading.Thread(target=complete, args=(lesson_id,)) for lesson_id in (1, 2)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    with app.app_context():
        from conversate.extensions import db
        from conversate.models import User
        refreshed = db.session.query(User).filter(User.id == user.id).one()
        assert sorted(refreshed.lessons_completed) == [1, 2]


def test_reset_clears_score_and_lessons(client, auth_headers, create_user):
    create_user(lessons=[1, 2, 3])
    body = client.post(ME + '/reset', headers=auth_headers()).get_json()
    assert body['score'] == 0
    assert body['lessons_completed'] == []
