import threading
from datetime import timedelta

import pytest
from sqlalchemy import select

from conversate.api.common import utcnow
from conversate.api.quiz import _build_quiz
from conversate.extensions import db
from conversate.models import QuizAttempt

START = '/api/me/quiz/start'
ANSWER = '/api/me/quiz/answer'
PAUSE = '/api/me/quiz/pause'
RESUME = '/api/me/quiz/resume'
SUBMIT = '/api/me/quiz/submit'
LEADERBOARD = '/api/leaderboard'


def _attempt_for(user_id):
    return db.session.scalars(select(QuizAttempt).where(QuizAttempt.user_id == user_id)).one()


def test_build_quiz_choices_are_unique_and_include_the_correct_answer():
    questions = _build_quiz()
    assert len(questions) == 50
    for q in questions:
        assert len(q['choices']) == 4
        assert len(set(q['choices'])) == 4
        assert q['correct'] in q['choices']


def test_start_issues_fifty_questions_without_answers(client, auth_headers, create_user):
    create_user()
    body = client.post(START, headers=auth_headers()).get_json()
    assert len(body['questions']) == 50
    for q in body['questions']:
        assert set(q.keys()) == {'it', 'choices'}
        assert len(q['choices']) == 4
    assert body['seconds_remaining'] <= 250


def test_concurrent_first_starts_returns_409_not_500(
    client, auth_headers, create_user, monkeypatch
):
    # Real threads rarely hit this window, and a restart that doesn't overlap
    # is valid. So start_quiz's check finds no attempt while a "concurrent"
    # request commits one first.
    import conversate.api.quiz as quiz_module

    user = create_user()

    def find_attempt_then_let_a_rival_insert(user_id):
        db.session.add(QuizAttempt(user_id=user_id, started_at=utcnow(), quiz_state=[]))
        db.session.commit()
        return None

    monkeypatch.setattr(quiz_module, '_find_attempt', find_attempt_then_let_a_rival_insert)

    response = client.post(START, headers=auth_headers(sub=user.auth0_sub))
    assert response.status_code == 409


def test_answer_out_of_order_is_409(client, auth_headers, create_user):
    create_user()
    client.post(START, headers=auth_headers())
    response = client.post(ANSWER, json={'index': 1, 'answer': 'x'}, headers=auth_headers())
    assert response.status_code == 409


def test_answer_grades_against_the_servers_answer_key(client, auth_headers, create_user):
    user = create_user()
    client.post(START, headers=auth_headers())
    attempt = _attempt_for(user.id)
    attempt.started_at = utcnow() - timedelta(seconds=10)
    db.session.commit()
    correct_word = attempt.quiz_state[0]['correct']

    right = client.post(ANSWER, json={'index': 0, 'answer': correct_word}, headers=auth_headers())
    assert right.get_json() == {'correct': True}

    wrong = client.post(
        ANSWER,
        json={'index': 1, 'answer': 'definitely not a real answer'},
        headers=auth_headers(),
    )
    assert wrong.get_json() == {'correct': False}

    assert _attempt_for(user.id).correct_count == 1


def test_answering_too_fast_is_429(client, auth_headers, create_user):
    # The UI shows each answer for 500ms, so only a script answers this fast.
    user = create_user()
    client.post(START, headers=auth_headers())
    attempt = _attempt_for(user.id)
    client.post(
        ANSWER,
        json={'index': 0, 'answer': attempt.quiz_state[0]['correct']},
        headers=auth_headers(),
    )
    response = client.post(
        ANSWER,
        json={'index': 1, 'answer': attempt.quiz_state[1]['correct']},
        headers=auth_headers(),
    )
    assert response.status_code == 429
    assert _attempt_for(user.id).next_index == 1


def test_answer_after_time_is_up_is_rejected(client, auth_headers, create_user):
    # Otherwise a client that never submits could keep scoring past the time
    # limit.
    user = create_user()
    client.post(START, headers=auth_headers())
    attempt = _attempt_for(user.id)
    attempt.started_at = utcnow() - timedelta(seconds=300)
    db.session.commit()

    response = client.post(
        ANSWER,
        json={'index': 0, 'answer': attempt.quiz_state[0]['correct']},
        headers=auth_headers(),
    )

    assert response.status_code == 409
    assert _attempt_for(user.id).correct_count == 0


def test_concurrent_guesses_for_one_question_only_score_once(
    app, client, auth_headers, create_user
):
    # Needs real concurrency: the index check alone rejects sequential repeats,
    # so the bug only shows when reads of next_index overlap.
    user = create_user()
    client.post(START, headers=auth_headers())
    attempt = _attempt_for(user.id)
    choices = attempt.quiz_state[0]['choices']
    headers = auth_headers()

    barrier = threading.Barrier(len(choices))
    statuses = [None] * len(choices)

    def guess(i, choice):
        barrier.wait()
        resp = client.post(ANSWER, json={'index': 0, 'answer': choice}, headers=headers)
        statuses[i] = resp.status_code

    threads = [
        threading.Thread(target=guess, args=(i, choice)) for i, choice in enumerate(choices)
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert statuses.count(200) == 1
    assert statuses.count(409) == len(choices) - 1
    with app.app_context():
        attempt = _attempt_for(user.id)
        assert attempt.next_index == 1
        assert attempt.correct_count <= 1


def test_answer_while_paused_is_rejected(client, auth_headers, create_user):
    user = create_user()
    client.post(START, headers=auth_headers())
    client.post(PAUSE, headers=auth_headers())
    attempt = _attempt_for(user.id)

    response = client.post(
        ANSWER,
        json={'index': 0, 'answer': attempt.quiz_state[0]['correct']},
        headers=auth_headers(),
    )

    assert response.status_code == 409
    assert _attempt_for(user.id).correct_count == 0


def test_pausing_again_after_the_limit_is_409(client, auth_headers, create_user):
    create_user()
    client.post(START, headers=auth_headers())
    client.post(PAUSE, headers=auth_headers())
    client.post(RESUME, headers=auth_headers())
    response = client.post(PAUSE, headers=auth_headers())
    assert response.status_code == 409


def test_pause_and_resume_works(client, auth_headers, create_user):
    create_user()
    client.post(START, headers=auth_headers())
    pause_body = client.post(PAUSE, headers=auth_headers()).get_json()
    assert pause_body['pauses_remaining'] == 0
    resume_response = client.post(RESUME, headers=auth_headers())
    assert resume_response.status_code == 200


def test_submit_uses_the_accumulated_correct_count(client, auth_headers, create_user):
    user = create_user()
    client.post(START, headers=auth_headers())
    attempt = _attempt_for(user.id)
    attempt.started_at = utcnow() - timedelta(seconds=10)
    db.session.commit()
    for i, q in enumerate(attempt.quiz_state[:3]):
        client.post(ANSWER, json={'index': i, 'answer': q['correct']}, headers=auth_headers())

    response = client.post(SUBMIT, headers=auth_headers())

    assert response.status_code == 200
    assert response.get_json()['score'] == 3


def test_quiz_times_are_stored_and_read_back_in_utc(client, auth_headers, create_user):
    user = create_user()
    client.post(START, headers=auth_headers())
    client.post(PAUSE, headers=auth_headers())
    attempt = _attempt_for(user.id)
    for value in (attempt.started_at, attempt.paused_at):
        assert value.utcoffset() == timedelta(0)
        assert abs((utcnow() - value).total_seconds()) < 60


def test_submit_consumes_the_attempt(client, auth_headers, create_user):
    user = create_user()
    client.post(START, headers=auth_headers())
    client.post(SUBMIT, headers=auth_headers())
    assert (
        db.session.scalars(select(QuizAttempt).where(QuizAttempt.user_id == user.id)).first()
        is None
    )


def test_worse_resubmission_does_not_overwrite_a_better_best(client, auth_headers, create_user):
    user = create_user()
    user.quiz_best_score = 45
    user.quiz_best_time_seconds = 60
    db.session.commit()

    client.post(START, headers=auth_headers())
    response = client.post(SUBMIT, headers=auth_headers())

    assert response.get_json()['is_new_best'] is False
    db.session.refresh(user)
    assert user.quiz_best_score == 45
    assert user.quiz_best_time_seconds == 60


def test_leaderboard_ranks_score_then_breaks_ties_with_time(client, auth_headers, create_user):
    a = create_user(sub='auth0|a', username='alice')
    b = create_user(sub='auth0|b', username='bob')
    c = create_user(sub='auth0|c', username='carla')
    a.quiz_best_score, a.quiz_best_time_seconds = 40, 120
    b.quiz_best_score, b.quiz_best_time_seconds = 40, 60
    c.quiz_best_score, c.quiz_best_time_seconds = 45, 200
    db.session.commit()

    body = client.get(LEADERBOARD, headers=auth_headers()).get_json()

    names = [row['username'] for row in body]
    # carla: highest score, wins outright. Between alice/bob's tied score,
    # bob's faster time wins the tiebreak.
    assert names == ['carla', 'bob', 'alice']


def test_practice_start_has_no_timer(client, auth_headers, create_user):
    user = create_user()
    body = client.post(START, json={'practice': True}, headers=auth_headers()).get_json()
    assert body['practice'] is True
    assert body['seconds_remaining'] is None
    assert body['pauses_remaining'] == 0
    assert _attempt_for(user.id).practice is True


def test_start_without_a_body_or_with_practice_false_is_timed(client, auth_headers, create_user):
    user = create_user()
    for kwargs in ({}, {'json': {'practice': False}}):
        body = client.post(START, headers=auth_headers(), **kwargs).get_json()
        assert body['practice'] is False
        assert body['seconds_remaining'] <= 250
        assert _attempt_for(user.id).practice is False


def test_start_rejects_a_practice_flag_that_isnt_a_boolean(client, auth_headers, create_user):
    create_user()
    response = client.post(START, json={'practice': 'yes'}, headers=auth_headers())
    assert response.status_code == 400


def test_practice_accepts_answers_past_the_time_limit(client, auth_headers, create_user):
    user = create_user()
    client.post(START, json={'practice': True}, headers=auth_headers())
    attempt = _attempt_for(user.id)
    attempt.started_at = utcnow() - timedelta(seconds=1000)
    db.session.commit()

    response = client.post(
        ANSWER,
        json={'index': 0, 'answer': attempt.quiz_state[0]['correct']},
        headers=auth_headers(),
    )

    assert response.status_code == 200
    assert response.get_json()['correct'] is True


@pytest.mark.parametrize('url', [PAUSE, RESUME])
def test_practice_has_no_timer_to_pause(client, auth_headers, create_user, url):
    create_user()
    client.post(START, json={'practice': True}, headers=auth_headers())
    response = client.post(url, headers=auth_headers())
    assert response.status_code == 409
    assert response.get_json() == {'error': 'A practice quiz has no timer'}


def test_practice_submit_leaves_the_best_score_alone(client, auth_headers, create_user):
    user = create_user()
    client.post(START, json={'practice': True}, headers=auth_headers())
    attempt = _attempt_for(user.id)
    attempt.started_at = utcnow() - timedelta(seconds=10)
    db.session.commit()
    client.post(
        ANSWER,
        json={'index': 0, 'answer': attempt.quiz_state[0]['correct']},
        headers=auth_headers(),
    )

    body = client.post(SUBMIT, headers=auth_headers()).get_json()

    assert body == {
        'score': 1,
        'time_seconds': body['time_seconds'],
        'is_new_best': False,
        'practice': True,
    }
    db.session.refresh(user)
    assert user.quiz_best_score is None
    assert (
        db.session.scalars(select(QuizAttempt).where(QuizAttempt.user_id == user.id)).first()
        is None
    )


@pytest.mark.parametrize(
    ('url', 'body'),
    [
        ('/api/me/quiz/answer', {'index': 0, 'answer': 'bread'}),
        ('/api/me/quiz/pause', None),
        ('/api/me/quiz/resume', None),
        ('/api/me/quiz/submit', None),
    ],
)
def test_quiz_actions_without_a_quiz_are_409(client, auth_headers, create_user, url, body):
    create_user()
    response = client.post(url, json=body, headers=auth_headers())
    assert response.status_code == 409
    assert response.get_json() == {'error': 'No quiz in progress; call /api/me/quiz/start first'}
