"""timezone-aware quiz times

Revision ID: 0008
Revises: 0007
Create Date: 2026-10-25 00:00:00.000000

Quiz start and pause times were stored without a timezone, holding UTC by
convention. timestamptz stores them as moments in time. AT TIME ZONE 'UTC'
reads the existing values as the UTC they always were, in both directions.
SQLite has no timezone type, so there it changes nothing.

"""

import sqlalchemy as sa
from alembic import op

revision = '0008'
down_revision = '0007'
branch_labels = None
depends_on = None

COLUMNS = ('started_at', 'paused_at')


def upgrade():
    if op.get_bind().dialect.name != 'postgresql':
        return
    for column in COLUMNS:
        op.alter_column(
            'quiz_attempt',
            column,
            type_=sa.DateTime(timezone=True),
            postgresql_using=f"{column} AT TIME ZONE 'UTC'",
        )


def downgrade():
    if op.get_bind().dialect.name != 'postgresql':
        return
    for column in COLUMNS:
        op.alter_column(
            'quiz_attempt',
            column,
            type_=sa.DateTime(),
            postgresql_using=f"{column} AT TIME ZONE 'UTC'",
        )
