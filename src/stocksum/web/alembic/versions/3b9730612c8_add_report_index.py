"""add report index

Revision ID: 3b9730612c8
Revises: 8240039fd3
Create Date: 2014-06-09 13:51:11.064514

"""

# revision identifiers, used by Alembic.
revision = '3b9730612c8'
down_revision = '8240039fd3'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_index(
        'ix_next_run',
        'report_crontab',
        ['next_run']
    )


def downgrade():
    raise NotImplemented()
