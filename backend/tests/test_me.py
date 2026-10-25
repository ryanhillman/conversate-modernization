import os
import threading
import time

import pytest
from sqlalchemy import select

from conversate.extensions import db
from conversate.models import QuizAttempt, User

ME = '/api/me'

VALID = {'username': 'tester'}


def test_requires_a_token(client):
    assert client.get(ME).status_code == 401
    assert client.post(ME, json=VALID).status_code == 401
    assert client.post(ME + '/reset').status_code == 401
    assert client.post(ME + '/lessons/1').status_code == 401


def test_create_stores_the_username(client, auth_headers):
    response = client.post(ME, json={'username': 'tester'}, headers=auth_headers())
    assert response.status_code == 201
    assert response.get_json()['username'] == 'tester'


def test_create_rejects_a_non_string_username(client, auth_headers):
    response = client.post(ME, json={'username': 123}, headers=auth_headers())
    assert response.status_code == 400


def test_create_rejects_a_duplicate(client, auth_headers, create_user):
    create_user(sub='auth0|test', username='tester')
    response = client.post(ME, json={'username': 'other'}, headers=auth_headers(sub='auth0|test'))
    assert response.status_code == 409


def test_get_without_profile_is_404(client, auth_headers):
    assert client.get(ME, headers=auth_headers()).status_code == 404


def test_get_resolves_to_the_authenticated_user_not_just_any_user(
    client, auth_headers, create_user
):
    create_user(sub='auth0|a', username='alice')
    create_user(sub='auth0|b', username='bob')
    body = client.get(ME, headers=auth_headers(sub='auth0|b')).get_json()
    assert body['username'] == 'bob'


def test_reset_does_not_touch_another_users_record(client, auth_headers, create_user):
    create_user(sub='auth0|a', username='alice', lessons=[1, 2])
    create_user(sub='auth0|b', username='bob', lessons=[3, 4])
    client.post(ME + '/reset', headers=auth_headers(sub='auth0|b'))
    untouched = client.get(ME, headers=auth_headers(sub='auth0|a')).get_json()
    assert untouched['lessons_completed'] == [1, 2]


def test_rename(client, auth_headers, create_user):
    create_user()
    response = client.put(ME, json={'username': 'renamed'}, headers=auth_headers())
    assert response.status_code == 200
    assert response.get_json()['username'] == 'renamed'


def test_rename_rejects_a_non_string_username(client, auth_headers, create_user):
    create_user()
    response = client.put(ME, json={'username': ['not', 'a', 'string']}, headers=auth_headers())
    assert response.status_code == 400


def test_rename_to_a_taken_username_is_409(client, auth_headers, create_user):
    create_user(sub='auth0|me', username='tester')
    create_user(sub='auth0|other', username='taken')
    assert (
        client.put(
            ME, json={'username': 'taken'}, headers=auth_headers(sub='auth0|me')
        ).status_code
        == 409
    )


def test_completing_a_lesson_twice_does_not_double_count(client, auth_headers, create_user):
    create_user()
    client.post(ME + '/lessons/1', headers=auth_headers())
    body = client.post(ME + '/lessons/1', headers=auth_headers()).get_json()
    assert body['lessons_completed'] == [1]


def test_completing_lesson_zero_is_400(client, auth_headers, create_user):
    create_user()
    assert client.post(ME + '/lessons/0', headers=auth_headers()).status_code == 400


def test_completing_a_lesson_past_the_sanity_bound_is_400(client, auth_headers, create_user):
    create_user()
    assert client.post(ME + '/lessons/1000', headers=auth_headers()).status_code == 400


@pytest.mark.skipif(
    not os.environ.get('TEST_DATABASE_URL'),
    reason='SQLite silently ignores SELECT ... FOR UPDATE (no FOR UPDATE clause '
    'is even generated), so the lock this test depends on has no effect '
    'there. Run with TEST_DATABASE_URL pointing at Postgres to exercise it.',
)
def test_concurrent_lesson_completions_do_not_lose_one(
    app, client, auth_headers, create_user, monkeypatch
):
    # lessons_completed is a JSON blob, so completing two different lessons
    # "at once" is a read-modify-write race: without a lock, both requests
    # can read the same starting list and the second commit overwrites the
    # first's addition.
    #
    # Just starting two threads together doesn't reliably hit that window —
    # each request does real work (JWT verification, etc.) before reaching
    # the locked query, so the two rarely arrive at the same instant. Instead,
    # make whichever request wins the lock hold it open (sleep before
    # returning, transaction still uncommitted) long enough that the other
    # request's own with_for_update() genuinely blocks on it at the database
    # level — a deterministic overlap instead of a timing hope.
    import conversate.api.accounts as accounts_module

    user = create_user()
    headers = auth_headers()

    real_lock = accounts_module._lock_user_for_update
    winner_assigned = threading.Lock()
    winner_decided = False

    def hold_lock_open(sub):
        nonlocal winner_decided
        record = real_lock(sub)
        with winner_assigned:
            is_winner = not winner_decided
            winner_decided = True
        if is_winner:
            time.sleep(0.5)
        return record

    monkeypatch.setattr(accounts_module, '_lock_user_for_update', hold_lock_open)

    def complete(lesson_id):
        client.post(f'{ME}/lessons/{lesson_id}', headers=headers)

    threads = [threading.Thread(target=complete, args=(lesson_id,)) for lesson_id in (1, 2)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    with app.app_context():
        from conversate.extensions import db
        from conversate.models import User

        refreshed = db.session.scalars(select(User).where(User.id == user.id)).one()
        assert sorted(refreshed.lessons_completed) == [1, 2]


def test_reset_clears_lessons(client, auth_headers, create_user):
    create_user(lessons=[1, 2, 3])
    body = client.post(ME + '/reset', headers=auth_headers()).get_json()
    assert body['lessons_completed'] == []


def test_reset_discards_an_in_progress_quiz_attempt(client, auth_headers, create_user):
    user = create_user()
    client.post('/api/me/quiz/start', headers=auth_headers())
    client.post(ME + '/reset', headers=auth_headers())

    assert (
        db.session.scalars(select(QuizAttempt).where(QuizAttempt.user_id == user.id)).first()
        is None
    )
    # Without the attempt, submitting can no longer record a bogus "new best".
    submit = client.post('/api/me/quiz/submit', headers=auth_headers())
    assert submit.status_code == 409


def test_delete_requires_a_token(client):
    assert client.delete(ME).status_code == 401


def test_delete_removes_the_account_and_any_quiz_attempt(client, auth_headers, create_user):
    user = create_user(lessons=[1, 2])
    user_id = user.id
    client.post('/api/me/quiz/start', headers=auth_headers())

    assert client.delete(ME, headers=auth_headers()).status_code == 204
    assert db.session.scalars(select(User).where(User.id == user_id)).first() is None
    assert (
        db.session.scalars(select(QuizAttempt).where(QuizAttempt.user_id == user_id)).first()
        is None
    )
    # The profile is gone, so the app treats them as a new user.
    assert client.get(ME, headers=auth_headers()).status_code == 404


def test_delete_does_not_touch_another_users_record(client, auth_headers, create_user):
    create_user(sub='auth0|a', username='alice')
    create_user(sub='auth0|b', username='bob')

    client.delete(ME, headers=auth_headers(sub='auth0|a'))

    assert client.get(ME, headers=auth_headers(sub='auth0|b')).status_code == 200


def test_delete_without_a_profile_is_404(client, auth_headers):
    assert client.delete(ME, headers=auth_headers()).status_code == 404
