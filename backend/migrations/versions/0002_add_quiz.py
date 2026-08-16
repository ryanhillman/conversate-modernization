"""add quiz

Revision ID: 0002
Revises: 0001
Create Date: 2026-08-09 00:00:00.000000

Adds the quiz leaderboard's best-attempt columns to user, and a quiz_attempt
table holding one in-flight, server-issued quiz per user (the answer key and
start time never leave the server).

"""
from alembic import op
import sqlalchemy as sa

revision = '0002'
down_revision = '0001'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('user', sa.Column('quiz_best_score', sa.Integer(), nullable=True))
    op.add_column('user', sa.Column('quiz_best_time_seconds', sa.Integer(), nullable=True))

    op.create_table(
        'quiz_attempt',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('started_at', sa.DateTime(), nullable=False),
        sa.Column('quiz_state', sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('uq_quiz_attempt_user_id', 'quiz_attempt', ['user_id'], unique=True)


def downgrade():
    op.drop_table('quiz_attempt')
    op.drop_column('user', 'quiz_best_time_seconds')
    op.drop_column('user', 'quiz_best_score')
