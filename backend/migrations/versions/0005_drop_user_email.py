"""drop user email

Revision ID: 0005
Revises: 0004
Create Date: 2026-10-21 00:00:00.000000

Email was profile data nothing ever read back — Profile shows Auth0's own
email instead. Drop the column rather than keep storing it unused.

"""

import sqlalchemy as sa
from alembic import op

revision = '0005'
down_revision = '0004'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('user') as batch_op:
        batch_op.drop_column('email')


def downgrade():
    op.add_column('user', sa.Column('email', sa.String(length=100), nullable=True))
