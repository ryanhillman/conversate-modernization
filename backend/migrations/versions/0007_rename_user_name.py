"""rename user_name to username

Revision ID: 0007
Revises: 0006
Create Date: 2026-10-25 00:00:00.000000

Renames the column, and its case-insensitive unique index, to match the
naming used everywhere else. RENAME COLUMN works the same on Postgres and
SQLite (3.25+), unlike Alembic's batch mode, which rebuilds the table on
SQLite. The index is dropped and recreated around the rename so its name and
expression both follow the new column. It's dropped only if it exists: on
SQLite, 0005's batch rebuild already lost it, and this restores it.

"""

import sqlalchemy as sa
from alembic import op

revision = '0007'
down_revision = '0006'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('DROP INDEX IF EXISTS uq_user_user_name_lower')
    op.execute('ALTER TABLE "user" RENAME COLUMN user_name TO username')
    op.create_index('uq_user_username_lower', 'user', [sa.text('lower(username)')], unique=True)


def downgrade():
    op.execute('DROP INDEX IF EXISTS uq_user_username_lower')
    op.execute('ALTER TABLE "user" RENAME COLUMN username TO user_name')
    op.create_index('uq_user_user_name_lower', 'user', [sa.text('lower(user_name)')], unique=True)
