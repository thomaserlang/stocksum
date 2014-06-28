"""added more report types 2

Revision ID: b67fa4736f
Revises: 13401065bd29
Create Date: 2014-06-18 19:57:38.058036

"""

# revision identifiers, used by Alembic.
revision = 'b67fa4736f'
down_revision = '13401065bd29'

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
        	id=6,
            name='Year to date',
            description='Generates a report containing your gains/losses for the year to date.',
            symbol='ytd',
        ),
    ])

def downgrade():
    raise NotImplemented()
