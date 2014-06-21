"""Add timezone to the user table

Revision ID: aaef03da98
Revises: 3b9730612c8
Create Date: 2014-06-09 14:36:14.229346

"""

# revision identifiers, used by Alembic.
revision = 'aaef03da98'
down_revision = '3b9730612c8'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column(
        'users',
        sa.Column('timezone', sa.String(50)),
    )


def downgrade():
    raise NotImplemented()
