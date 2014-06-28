"""added more report types

Revision ID: 13401065bd29
Revises: aaef03da98
Create Date: 2014-06-14 22:22:12.048324

"""

# revision identifiers, used by Alembic.
revision = '13401065bd29'
down_revision = 'aaef03da98'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column


def upgrade():
    report_types = table('report_types',
        column('id', sa.Integer),
        column('name', sa.String(60)),
        column('description', sa.Text),
        column('symbol', sa.String(40))
    )
    op.bulk_insert(report_types, [
        dict(
            id=2,
            name='1 week',
            description='Generates a report containing your gains/losses for the latest week.',
            symbol='1-week'
        ),
        dict(
            id=3,
            name='3 months',
            description='Generates a report containing your gains/losses for the latest 3 months.',
            symbol='3-months'
        ),
        dict(
            id=4,
            name='6 months',
            description='Generates a report containing your gains/losses for the latest 6 months.',
            symbol='6-months'
        ),
        dict(
            id=5,
            name='1 year',
            description='Generates a report containing your gains/losses for the latest year.',
            symbol='1-year'
        ),
    ])

def downgrade():
    raise NotImplemented()
