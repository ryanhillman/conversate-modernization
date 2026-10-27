"""practice quizzes

Revision ID: 0002
Revises: 0001_v2
Create Date: 2026-10-27 00:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

revision = '0002'
down_revision = '0001_v2'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'quiz_attempt',
        sa.Column('practice', sa.Boolean(), nullable=False, server_default=sa.false()),
    )


def downgrade():
    op.drop_column('quiz_attempt', 'practice')
