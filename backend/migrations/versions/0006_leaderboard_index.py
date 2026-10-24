"""leaderboard index

Revision ID: 0006
Revises: 0005
Create Date: 2026-10-24 00:00:00.000000

An index matching the leaderboard query's ORDER BY (best score descending,
then time, then id), so the top rows can be read in order from the index
instead of scanning and sorting the whole table. Partial, because the
leaderboard only reads users who have a best score.

"""

import sqlalchemy as sa
from alembic import op

revision = '0006'
down_revision = '0005'
branch_labels = None
depends_on = None


def upgrade():
    op.create_index(
        'ix_user_leaderboard',
        'user',
        [sa.text('quiz_best_score DESC'), 'quiz_best_time_seconds', 'id'],
        postgresql_where=sa.text('quiz_best_score IS NOT NULL'),
        sqlite_where=sa.text('quiz_best_score IS NOT NULL'),
    )


def downgrade():
    op.drop_index('ix_user_leaderboard', table_name='user')
