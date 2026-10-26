from datetime import UTC, datetime

from sqlalchemy import JSON, DateTime, ForeignKey, String, text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import TypeDecorator

from .extensions import db


class UTCDateTime(TypeDecorator):
    """A timezone-aware datetime, always returned in UTC. Postgres returns it
    in the session's timezone; SQLite returns it without one."""

    impl = DateTime(timezone=True)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        return value.astimezone(UTC) if value is not None else None

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return value.replace(tzinfo=UTC) if value.tzinfo is None else value.astimezone(UTC)


class User(db.Model):
    # Not 'user', which is a reserved word in Postgres.
    __tablename__ = 'account'

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
        db.Index('uq_account_auth0_sub', auth0_sub, unique=True),
        db.Index('uq_account_username_lower', db.func.lower(username), unique=True),
        # Matches the leaderboard's ORDER BY. Partial, because the leaderboard
        # only ever reads users who have a best score.
        db.Index(
            'ix_account_leaderboard',
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
    """An in-flight quiz: the server's private answer key and start time for
    one user. Written by /api/me/quiz/start, and deleted by /api/me/quiz/submit,
    a reset, or account deletion. Never serialized to the client."""

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('account.id'))
    started_at: Mapped[datetime] = mapped_column(UTCDateTime)
    quiz_state: Mapped[list[dict]] = mapped_column(JSON)
    next_index: Mapped[int] = mapped_column(default=0)
    correct_count: Mapped[int] = mapped_column(default=0)
    paused_at: Mapped[datetime | None] = mapped_column(UTCDateTime)
    pauses_used: Mapped[int] = mapped_column(default=0)

    __table_args__ = (db.Index('uq_quiz_attempt_user_id', user_id, unique=True),)
