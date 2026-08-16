"""quiz pause limit

Revision ID: 0004
Revises: 0003
Create Date: 2026-08-10 00:00:00.000000

Tracks how many times an attempt has been paused, so /pause can enforce a
one-pause-per-quiz limit.

"""
from alembic import op
import sqlalchemy as sa

revision = '0004'
down_revision = '0003'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'quiz_attempt',
        sa.Column('pauses_used', sa.Integer(), nullable=False, server_default='0'),
    )
    with op.batch_alter_table('quiz_attempt') as batch_op:
        batch_op.alter_column('pauses_used', server_default=None)


def downgrade():
    op.drop_column('quiz_attempt', 'pauses_used')
