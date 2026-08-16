"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-07-24 00:00:00.000000

Single baseline matching the models: accounts keyed on the Auth0 subject,
email as optional profile data, and case-insensitive username uniqueness.

"""
from alembic import op
import sqlalchemy as sa

revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'user',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('auth0_sub', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=100), nullable=True),
        sa.Column('user_name', sa.String(length=100), nullable=False),
        sa.Column('lessons_completed', sa.JSON(), nullable=False,
                  server_default=sa.text("'[]'")),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('uq_user_auth0_sub', 'user', ['auth0_sub'], unique=True)
    op.create_index('uq_user_user_name_lower', 'user',
                    [sa.text('lower(user_name)')], unique=True)


def downgrade():
    op.drop_table('user')
