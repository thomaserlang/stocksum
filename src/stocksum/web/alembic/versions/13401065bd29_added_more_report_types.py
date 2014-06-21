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
from stocksum.web import models
from stocksum.web.decorators import new_session


def upgrade():
    with new_session() as session:
        report_type = models.Report_type(
            name='1 week',
            description='Generates a report containing your gains/losses for the latest week.',
            symbol='1-week'
        )
        session.add(report_type)
        report_type = models.Report_type(
            name='1 month',
            description='Generates a report containing your gains/losses for the latest month.',
            symbol='1-month'
        )
        session.add(report_type)
        report_type = models.Report_type(
            name='3 months',
            description='Generates a report containing your gains/losses for the latest 3 months.',
            symbol='3-months'
        )
        session.add(report_type)
        report_type = models.Report_type(
            name='6 months',
            description='Generates a report containing your gains/losses for the latest 6 months.',
            symbol='6-months'
        )
        session.add(report_type)
        report_type = models.Report_type(
            name='1 year',
            description='Generates a report containing your gains/losses for the latest year.',
            symbol='1-year'
        )
        session.add(report_type)
        session.commit()


def downgrade():
    raise NotImplemented()
