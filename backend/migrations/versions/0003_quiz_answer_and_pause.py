"""quiz answer and pause

Revision ID: 0003
Revises: 0002
Create Date: 2026-08-10 00:00:00.000000

Adds per-question grading state (next_index, correct_count) and pause support
(paused_at) to quiz_attempt, so answers can be graded and colored one at a
time instead of only at final submission.

"""
from alembic import op
import sqlalchemy as sa

revision = '0003'
down_revision = '0002'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'quiz_attempt',
        sa.Column('next_index', sa.Integer(), nullable=False, server_default='0'),
    )
    op.add_column(
        'quiz_attempt',
        sa.Column('correct_count', sa.Integer(), nullable=False, server_default='0'),
    )
    op.add_column('quiz_attempt', sa.Column('paused_at', sa.DateTime(), nullable=True))
    with op.batch_alter_table('quiz_attempt') as batch_op:
        batch_op.alter_column('next_index', server_default=None)
        batch_op.alter_column('correct_count', server_default=None)


def downgrade():
    op.drop_column('quiz_attempt', 'paused_at')
    op.drop_column('quiz_attempt', 'correct_count')
    op.drop_column('quiz_attempt', 'next_index')
