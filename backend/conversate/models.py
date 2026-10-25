from .extensions import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    auth0_sub = db.Column(db.String(255), nullable=False)
    username = db.Column(db.String(100), nullable=False)
    lessons_completed = db.Column(
        db.JSON, nullable=False, default=list, server_default=db.text("'[]'")
    )
    quiz_best_score = db.Column(db.Integer, nullable=True)
    quiz_best_time_seconds = db.Column(db.Integer, nullable=True)

    # Identity is the Auth0 subject, so that's the unique key. username is
    # compared case-insensitively in the app, so it's enforced the same way in
    # the database.
    __table_args__ = (
        db.Index('uq_user_auth0_sub', auth0_sub, unique=True),
        db.Index('uq_user_username_lower', db.func.lower(username), unique=True),
        # Matches the leaderboard's ORDER BY. Partial, because the leaderboard
        # only ever reads users who have a best score.
        db.Index(
            'ix_user_leaderboard',
            quiz_best_score.desc(),
            quiz_best_time_seconds,
            id,
            postgresql_where=quiz_best_score.is_not(None),
            sqlite_where=quiz_best_score.is_not(None),
        ),
    )

    def __init__(self, auth0_sub, username):
        self.auth0_sub = auth0_sub
        self.username = username

    def serialize(self):
        return {
            'id': self.id,
            'username': self.username,
            'lessons_completed': self.lessons_completed or [],
            'quiz_best_score': self.quiz_best_score,
            'quiz_best_time_seconds': self.quiz_best_time_seconds,
        }


class QuizAttempt(db.Model):
    """An in-flight, single-use quiz: the server's private answer key and start
    time for one user. Created by /api/me/quiz/start, consumed and deleted by
    /api/me/quiz/submit. Never serialized to the client."""

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    started_at = db.Column(db.DateTime, nullable=False)
    quiz_state = db.Column(db.JSON, nullable=False)
    next_index = db.Column(db.Integer, nullable=False, default=0)
    correct_count = db.Column(db.Integer, nullable=False, default=0)
    paused_at = db.Column(db.DateTime, nullable=True)
    pauses_used = db.Column(db.Integer, nullable=False, default=0)

    __table_args__ = (db.Index('uq_quiz_attempt_user_id', user_id, unique=True),)
