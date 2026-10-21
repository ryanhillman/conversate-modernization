from datetime import timedelta

from conversate.api.quiz import _build_quiz
from conversate.api.common import _utcnow
from conversate.extensions import db
from conversate.models import QuizAttempt

START = '/api/me/quiz/start'
ANSWER = '/api/me/quiz/answer'
PAUSE = '/api/me/quiz/pause'
RESUME = '/api/me/quiz/resume'
SUBMIT = '/api/me/quiz/submit'
LEADERBOARD = '/api/leaderboard'


def _attempt_for(user_id):
    return db.session.query(QuizAttempt).filter(QuizAttempt.user_id == user_id).one()


def test_build_quiz_choices_are_unique_and_include_the_correct_answer():
    questions = _build_quiz()
    assert len(questions) == 50
    for q in questions:
        assert len(q['choices']) == 4
        assert len(set(q['choices'])) == 4
        assert q['correct'] in q['choices']


def test_start_requires_a_token(client):
    assert client.post(START).status_code == 401


def test_start_issues_fifty_questions_without_answers(client, auth_headers, create_user):
    create_user()
    body = client.post(START, headers=auth_headers()).get_json()
    assert len(body['questions']) == 50
    for q in body['questions']:
        assert set(q.keys()) == {'it', 'choices'}
        assert len(q['choices']) == 4
    assert body['seconds_remaining'] <= 250


def test_answer_out_of_order_is_409(client, auth_headers, create_user):
    create_user()
    client.post(START, headers=auth_headers())
    response = client.post(ANSWER, json={'index': 1, 'answer': 'x'}, headers=auth_headers())
    assert response.status_code == 409


def test_answer_grades_against_the_servers_answer_key(client, auth_headers, create_user):
    user = create_user()
    client.post(START, headers=auth_headers())
    attempt = _attempt_for(user.id)
    correct_word = attempt.quiz_state[0]['correct']

    right = client.post(
        ANSWER, json={'index': 0, 'answer': correct_word}, headers=auth_headers()
    )
    assert right.get_json() == {'correct': True}

    wrong = client.post(
        ANSWER, json={'index': 1, 'answer': 'definitely not a real answer'},
        headers=auth_headers(),
    )
    assert wrong.get_json() == {'correct': False}

    assert _attempt_for(user.id).correct_count == 1


def test_answer_after_time_is_up_is_rejected(client, auth_headers, create_user):
    # Without this, a client that never calls /submit (a bug, a backgrounded
    # tab, or a raw client bypassing the timed UI entirely) could keep
    # answering indefinitely past the 250s cap and still have every answer
    # graded — only the *reported* time was ever capped, not the actual
    # opportunity to keep scoring.
    user = create_user()
    client.post(START, headers=auth_headers())
    attempt = _attempt_for(user.id)
    attempt.started_at = _utcnow() - timedelta(seconds=300)
    db.session.commit()

    response = client.post(
        ANSWER, json={'index': 0, 'answer': attempt.quiz_state[0]['correct']},
        headers=auth_headers(),
    )

    assert response.status_code == 409
    assert _attempt_for(user.id).correct_count == 0


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
    for i, q in enumerate(attempt.quiz_state[:3]):
        client.post(
            ANSWER, json={'index': i, 'answer': q['correct']}, headers=auth_headers()
        )

    response = client.post(SUBMIT, headers=auth_headers())

    assert response.status_code == 200
    assert response.get_json()['score'] == 3


def test_submit_consumes_the_attempt(client, auth_headers, create_user):
    user = create_user()
    client.post(START, headers=auth_headers())
    client.post(SUBMIT, headers=auth_headers())
    assert db.session.query(QuizAttempt).filter(QuizAttempt.user_id == user.id).count() == 0


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
    a = create_user(sub='auth0|a', user_name='alice')
    b = create_user(sub='auth0|b', user_name='bob')
    c = create_user(sub='auth0|c', user_name='carla')
    a.quiz_best_score, a.quiz_best_time_seconds = 40, 120
    b.quiz_best_score, b.quiz_best_time_seconds = 40, 60
    c.quiz_best_score, c.quiz_best_time_seconds = 45, 200
    db.session.commit()

    body = client.get(LEADERBOARD, headers=auth_headers()).get_json()

    names = [row['user_name'] for row in body]
    # carla: highest score, wins outright. Between alice/bob's tied score,
    # bob's faster time wins the tiebreak.
    assert names == ['carla', 'bob', 'alice']
