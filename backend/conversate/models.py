from datetime import UTC, datetime

from sqlalchemy import JSON, DateTime, ForeignKey, String, false, text
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

    # Accounts are keyed by Auth0 subject. Usernames are unique ignoring case,
    # as the app compares them.
    __table_args__ = (
        db.Index('uq_account_auth0_sub', auth0_sub, unique=True),
        db.Index('uq_account_username_lower', db.func.lower(username), unique=True),
        # Matches the leaderboard's ORDER BY; partial, since it only reads
        # accounts with a best score.
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
            'username': self.username,
            'lessons_completed': self.lessons_completed,
            'quiz_best_score': self.quiz_best_score,
            'quiz_best_time_seconds': self.quiz_best_time_seconds,
        }


class QuizAttempt(db.Model):
    """One user's in-flight quiz, with an answer key that never leaves the
    server. Written by /api/me/quiz/start; deleted by submit, a reset, or
    account deletion."""

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('account.id'))
    started_at: Mapped[datetime] = mapped_column(UTCDateTime)
    quiz_state: Mapped[list[dict]] = mapped_column(JSON)
    next_index: Mapped[int] = mapped_column(default=0)
    correct_count: Mapped[int] = mapped_column(default=0)
    paused_at: Mapped[datetime | None] = mapped_column(UTCDateTime)
    pauses_used: Mapped[int] = mapped_column(default=0)
    # Untimed, and never counts toward the leaderboard.
    practice: Mapped[bool] = mapped_column(default=False, server_default=false())

    # Each start is a new row whose id names the quiz, so ids must never come
    # back; Postgres guarantees that, SQLite only with this.
    __table_args__ = (
        db.Index('uq_quiz_attempt_user_id', user_id, unique=True),
        {'sqlite_autoincrement': True},
    )
