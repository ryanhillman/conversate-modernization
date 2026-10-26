"""baseline

Revision ID: 0001_v2
Revises:
Create Date: 2026-10-26 00:00:00.000000

The 2.0.0 schema in one step, replacing the earlier history (1.0.0's baseline
and the changes after it). A database created by those migrations can't be
upgraded from here; recreate it.

"""

import sqlalchemy as sa
from alembic import op

revision = '0001_v2'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'account',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('auth0_sub', sa.String(length=255), nullable=False),
        sa.Column('username', sa.String(length=100), nullable=False),
        sa.Column('lessons_completed', sa.JSON(), nullable=False, server_default=sa.text("'[]'")),
        sa.Column('quiz_best_score', sa.Integer(), nullable=True),
        sa.Column('quiz_best_time_seconds', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('uq_account_auth0_sub', 'account', ['auth0_sub'], unique=True)
    op.create_index(
        'uq_account_username_lower', 'account', [sa.text('lower(username)')], unique=True
    )
    op.create_index(
        'ix_account_leaderboard',
        'account',
        [sa.text('quiz_best_score DESC'), 'quiz_best_time_seconds', 'id'],
        postgresql_where=sa.text('quiz_best_score IS NOT NULL'),
        sqlite_where=sa.text('quiz_best_score IS NOT NULL'),
    )

    op.create_table(
        'quiz_attempt',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('quiz_state', sa.JSON(), nullable=False),
        sa.Column('next_index', sa.Integer(), nullable=False),
        sa.Column('correct_count', sa.Integer(), nullable=False),
        sa.Column('paused_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('pauses_used', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['account.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('uq_quiz_attempt_user_id', 'quiz_attempt', ['user_id'], unique=True)


def downgrade():
    op.drop_table('quiz_attempt')
    op.drop_table('account')
