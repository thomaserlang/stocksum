"""Add users table

Revision ID: 3c4f298b063
Revises: None
Create Date: 2014-05-30 16:47:01.992457

"""

# revision identifiers, used by Alembic.
revision = '3c4f298b063'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('name', sa.String(200), unique=True),
        sa.Column('email', sa.String(200), unique=True),
        sa.Column('created', sa.DateTime),
    )


def downgrade():
    raise NotImplemented()
