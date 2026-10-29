import threading
from datetime import timedelta

import pytest
from sqlalchemy import select

from conversate.api import quiz as quiz_module
from conversate.api.common import utcnow
from conversate.api.quiz import QUIZ_TIME_LIMIT_SECONDS, _build_quiz
from conversate.extensions import db
from conversate.models import QuizAttempt
from conversate.quiz_data import QUIZ_WORDS

START = '/api/me/quiz/start'
ANSWER = '/api/me/quiz/answer'
PAUSE = '/api/me/quiz/pause'
RESUME = '/api/me/quiz/resume'
SUBMIT = '/api/me/quiz/submit'
LEADERBOARD = '/api/leaderboard'
REPLACED = {'error': 'A newer start replaced this quiz', 'code': 'replaced'}


def _attempt_for(user_id):
    return db.session.scalars(select(QuizAttempt).where(QuizAttempt.user_id == user_id)).one()


@pytest.fixture
def start_quiz(client, auth_headers):
    """Starts a quiz and returns it, each of its actions sending the attempt_id
    that start gave out."""

    class Quiz:
        def __init__(self, sub='auth0|test', **body):
            self.headers = auth_headers(sub)
            self.response = client.post(START, json=body or None, headers=self.headers)
            self.body = self.response.get_json()
            self.attempt_id = self.body.get('attempt_id')

        def post(self, url, **fields):
            body = {'attempt_id': self.attempt_id, **fields}
            return client.post(url, json=body, headers=self.headers)

        def answer(self, index, answer):
            return self.post(ANSWER, index=index, answer=answer)

        def pause(self):
            return self.post(PAUSE)

        def resume(self):
            return self.post(RESUME)

        def submit(self):
            return self.post(SUBMIT)

    return Quiz


def test_build_quiz_asks_every_word_once_with_unique_choices_including_the_answer():
    questions = _build_quiz()
    assert sorted(q['it'] for q in questions) == sorted(w['it'] for w in QUIZ_WORDS)
    for q in questions:
        assert len(q['choices']) == 4
        assert len(set(q['choices'])) == 4
        assert q['correct'] in q['choices']


def test_no_quiz_word_is_its_own_answer():
    assert [w for w in QUIZ_WORDS if w['it'] == w['en']] == []


def test_start_issues_every_question_without_its_answer(start_quiz, create_user):
    create_user()
    body = start_quiz().body
    assert isinstance(body['attempt_id'], int)
    assert len(body['questions']) == len(QUIZ_WORDS)
    for q in body['questions']:
        assert set(q.keys()) == {'it', 'choices'}
        assert len(q['choices']) == 4
    assert body['seconds_remaining'] <= 250


def test_concurrent_first_starts_returns_409_not_500(start_quiz, create_user, monkeypatch):
    # Real threads rarely hit this window, and a restart that doesn't overlap
    # is valid. So a "concurrent" start commits its row between ours clearing
    # the old one and inserting the new.
    user = create_user()
    discard = quiz_module._discard_attempt

    def discard_then_let_a_rival_insert(user_id):
        discard(user_id)
        db.session.add(QuizAttempt(user_id=user_id, started_at=utcnow(), quiz_state=[]))
        db.session.commit()

    monkeypatch.setattr(quiz_module, '_discard_attempt', discard_then_let_a_rival_insert)

    assert start_quiz(sub=user.auth0_sub).response.status_code == 409


def test_a_newer_start_replaces_the_quiz_and_refuses_the_old_ones_actions(start_quiz, create_user):
    create_user()
    old = start_quiz()
    new = start_quiz()
    assert new.attempt_id != old.attempt_id

    for response in (old.answer(0, 'x'), old.pause(), old.resume(), old.submit()):
        assert response.status_code == 409
        assert response.get_json() == REPLACED
    assert new.pause().status_code == 200


def test_quiz_actions_need_an_integer_attempt_id(client, auth_headers, start_quiz, create_user):
    create_user()
    start_quiz()
    for body in ({}, {'attempt_id': '1'}):
        response = client.post(SUBMIT, json=body, headers=auth_headers())
        assert response.status_code == 400
        assert response.get_json() == {'error': 'attempt_id must be an integer'}


def test_answer_out_of_order_is_409(start_quiz, create_user):
    create_user()
    response = start_quiz().answer(1, 'x')
    assert response.status_code == 409
    assert response.get_json()['code'] == 'out_of_sync'


def test_answer_grades_against_the_servers_answer_key(start_quiz, create_user):
    user = create_user()
    quiz = start_quiz()
    attempt = _attempt_for(user.id)
    attempt.started_at = utcnow() - timedelta(seconds=10)
    db.session.commit()
    correct_word = attempt.quiz_state[0]['correct']

    assert quiz.answer(0, correct_word).get_json() == {'correct': True}
    assert quiz.answer(1, 'definitely not a real answer').get_json() == {'correct': False}
    assert _attempt_for(user.id).correct_count == 1


def test_answering_too_fast_is_429(start_quiz, create_user):
    # The UI shows each answer for 500ms, so only a script answers this fast.
    user = create_user()
    quiz = start_quiz()
    attempt = _attempt_for(user.id)
    quiz.answer(0, attempt.quiz_state[0]['correct'])

    response = quiz.answer(1, attempt.quiz_state[1]['correct'])

    assert response.status_code == 429
    assert _attempt_for(user.id).next_index == 1


def test_answer_after_time_is_up_is_rejected(start_quiz, create_user):
    # Otherwise a client that never submits could keep scoring past the time
    # limit.
    user = create_user()
    quiz = start_quiz()
    attempt = _attempt_for(user.id)
    attempt.started_at = utcnow() - timedelta(seconds=300)
    db.session.commit()

    response = quiz.answer(0, attempt.quiz_state[0]['correct'])

    assert response.status_code == 409
    assert _attempt_for(user.id).correct_count == 0


def test_concurrent_guesses_for_one_question_only_score_once(app, start_quiz, create_user):
    # Needs real concurrency: the index check alone rejects sequential repeats,
    # so the bug only shows when reads of next_index overlap.
    user = create_user()
    quiz = start_quiz()
    choices = _attempt_for(user.id).quiz_state[0]['choices']

    barrier = threading.Barrier(len(choices))
    statuses = [None] * len(choices)

    def guess(i, choice):
        barrier.wait()
        statuses[i] = quiz.answer(0, choice).status_code

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
        assert _attempt_for(user.id).next_index == 1


def test_answer_while_paused_is_rejected(start_quiz, create_user):
    user = create_user()
    quiz = start_quiz()
    quiz.pause()
    attempt = _attempt_for(user.id)

    response = quiz.answer(0, attempt.quiz_state[0]['correct'])

    assert response.status_code == 409
    assert _attempt_for(user.id).correct_count == 0


def test_pausing_again_after_the_limit_is_409(start_quiz, create_user):
    create_user()
    quiz = start_quiz()
    quiz.pause()
    quiz.resume()
    assert quiz.pause().status_code == 409


def test_a_pause_of_any_length_stops_the_clock(start_quiz, create_user):
    user = create_user()
    quiz = start_quiz()
    assert quiz.pause().get_json()['pauses_remaining'] == 0
    attempt = _attempt_for(user.id)
    attempt.paused_at -= timedelta(minutes=20)
    attempt.started_at -= timedelta(minutes=20)
    db.session.commit()

    resume_body = quiz.resume().get_json()

    assert resume_body['seconds_remaining'] > QUIZ_TIME_LIMIT_SECONDS - 5


def test_submit_uses_the_accumulated_correct_count(start_quiz, create_user):
    user = create_user()
    quiz = start_quiz()
    attempt = _attempt_for(user.id)
    attempt.started_at = utcnow() - timedelta(seconds=10)
    db.session.commit()
    for i, q in enumerate(attempt.quiz_state[:3]):
        quiz.answer(i, q['correct'])

    response = quiz.submit()

    assert response.status_code == 200
    assert response.get_json()['score'] == 3


def test_quiz_times_are_stored_and_read_back_in_utc(start_quiz, create_user):
    user = create_user()
    start_quiz().pause()
    attempt = _attempt_for(user.id)
    for value in (attempt.started_at, attempt.paused_at):
        assert value.utcoffset() == timedelta(0)
        assert abs((utcnow() - value).total_seconds()) < 60


def test_submit_consumes_the_attempt(start_quiz, create_user):
    user = create_user()
    start_quiz().submit()
    assert (
        db.session.scalars(select(QuizAttempt).where(QuizAttempt.user_id == user.id)).first()
        is None
    )


def test_nothing_right_is_not_a_best_and_stays_off_the_leaderboard(
    client, auth_headers, start_quiz, create_user
):
    user = create_user()

    body = start_quiz().submit().get_json()

    assert body['score'] == 0
    assert body['is_new_best'] is False
    db.session.refresh(user)
    assert user.quiz_best_score is None
    assert client.get(LEADERBOARD, headers=auth_headers()).get_json() == []


def test_worse_resubmission_does_not_overwrite_a_better_best(start_quiz, create_user):
    user = create_user()
    user.quiz_best_score = 45
    user.quiz_best_time_seconds = 60
    db.session.commit()

    response = start_quiz().submit()

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


def test_practice_start_has_no_timer(start_quiz, create_user):
    user = create_user()
    body = start_quiz(practice=True).body
    assert body['practice'] is True
    assert body['seconds_remaining'] is None
    assert body['pauses_remaining'] == 0
    assert _attempt_for(user.id).practice is True


def test_start_without_a_body_or_with_practice_false_is_timed(start_quiz, create_user):
    user = create_user()
    for body in ({}, {'practice': False}):
        started = start_quiz(**body).body
        assert started['practice'] is False
        assert started['seconds_remaining'] <= 250
        assert _attempt_for(user.id).practice is False


def test_start_rejects_a_practice_flag_that_isnt_a_boolean(start_quiz, create_user):
    create_user()
    assert start_quiz(practice='yes').response.status_code == 400


def test_practice_accepts_answers_past_the_time_limit(start_quiz, create_user):
    user = create_user()
    quiz = start_quiz(practice=True)
    attempt = _attempt_for(user.id)
    attempt.started_at = utcnow() - timedelta(seconds=1000)
    db.session.commit()

    response = quiz.answer(0, attempt.quiz_state[0]['correct'])

    assert response.status_code == 200
    assert response.get_json()['correct'] is True


@pytest.mark.parametrize('action', ['pause', 'resume'])
def test_practice_has_no_timer_to_pause(start_quiz, create_user, action):
    create_user()
    response = getattr(start_quiz(practice=True), action)()
    assert response.status_code == 409
    assert response.get_json() == {'error': 'A practice quiz has no timer'}


def test_practice_submit_leaves_the_best_score_alone(start_quiz, create_user):
    user = create_user()
    quiz = start_quiz(practice=True)
    attempt = _attempt_for(user.id)
    attempt.started_at = utcnow() - timedelta(seconds=10)
    db.session.commit()
    quiz.answer(0, attempt.quiz_state[0]['correct'])

    body = quiz.submit().get_json()

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
    ('url', 'fields'),
    [(ANSWER, {'index': 0, 'answer': 'bread'}), (PAUSE, {}), (RESUME, {}), (SUBMIT, {})],
)
def test_quiz_actions_without_a_quiz_are_409(client, auth_headers, create_user, url, fields):
    create_user()
    response = client.post(url, json={'attempt_id': 1, **fields}, headers=auth_headers())
    assert response.status_code == 409
    assert response.get_json() == {'error': 'No quiz in progress; call /api/me/quiz/start first'}
