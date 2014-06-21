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
from stocksum.web import models
from stocksum.web.decorators import new_session


def upgrade():
    with new_session() as session:
        report_type = models.Report_type(
            name='Year to date',
            description='Generates a report containing your gains/losses for the year to date.',
            symbol='ytd'
        )
        session.add(report_type)
        session.commit()


def downgrade():
    raise NotImplemented()
