from .extensions import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    auth0_sub = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(100), nullable=True)
    user_name = db.Column(db.String(100), nullable=False)
    lessons_completed = db.Column(db.JSON, nullable=False, default=list, server_default=db.text("'[]'"))
    quiz_best_score = db.Column(db.Integer, nullable=True)
    quiz_best_time_seconds = db.Column(db.Integer, nullable=True)

    # Identity is the Auth0 subject, so that's the unique key. user_name is
    # compared case-insensitively in the app, so it's enforced the same way in
    # the database. Email is profile data now, not an identity, so it isn't
    # unique.
    __table_args__ = (
        db.Index('uq_user_auth0_sub', auth0_sub, unique=True),
        db.Index('uq_user_user_name_lower', db.func.lower(user_name), unique=True),
    )

    def __init__(self, auth0_sub, email, user_name):
        self.auth0_sub = auth0_sub
        self.email = email
        self.user_name = user_name

    def serialize(self):
        lessons = self.lessons_completed or []
        return {
            'id': self.id,
            'user_name': self.user_name,
            'email': self.email,
            'score': len(lessons),
            'lessons_completed': lessons,
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

    __table_args__ = (
        db.Index('uq_quiz_attempt_user_id', user_id, unique=True),
    )
