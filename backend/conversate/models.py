from datetime import datetime

from sqlalchemy import JSON, ForeignKey, String, text
from sqlalchemy.orm import Mapped, mapped_column

from .extensions import db


class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    auth0_sub: Mapped[str] = mapped_column(String(255))
    username: Mapped[str] = mapped_column(String(100))
    lessons_completed: Mapped[list[int]] = mapped_column(
        JSON, default=list, server_default=text("'[]'")
    )
    quiz_best_score: Mapped[int | None] = mapped_column()
    quiz_best_time_seconds: Mapped[int | None] = mapped_column()

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

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
    started_at: Mapped[datetime]
    quiz_state: Mapped[list[dict]] = mapped_column(JSON)
    next_index: Mapped[int] = mapped_column(default=0)
    correct_count: Mapped[int] = mapped_column(default=0)
    paused_at: Mapped[datetime | None]
    pauses_used: Mapped[int] = mapped_column(default=0)

    __table_args__ = (db.Index('uq_quiz_attempt_user_id', user_id, unique=True),)
