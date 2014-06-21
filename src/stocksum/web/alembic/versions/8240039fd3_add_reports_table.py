"""add reports table

Revision ID: 8240039fd3
Revises: 1c9398290e4
Create Date: 2014-06-06 19:38:39.487416

"""

# revision identifiers, used by Alembic.
revision = '8240039fd3'
down_revision = '1c9398290e4'

from alembic import op
import sqlalchemy as sa
from stocksum.web import models
from stocksum.web.decorators import new_session


def upgrade():
    op.create_table(
        'report_types',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('name', sa.String(60)),
        sa.Column('description', sa.Text),
        sa.Column('symbol', sa.String(40), unique=True),
    )

    with new_session() as session:
        report_type = models.Report_type(
            name='Daily',
            description='Generates a report containing your gains/losses for the day.',
            symbol='daily'
        )
        session.add(report_type)
        session.commit()

    op.create_table(
        'reports',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('portfolio_id', sa.Integer, sa.ForeignKey('portfolios.id', onupdate='cascade', ondelete='cascade')),
        sa.Column('report_type_id', sa.Integer, sa.ForeignKey('report_types.id', onupdate='cascade', ondelete='cascade')),
        sa.Column('report_crontab_id', sa.Integer, sa.ForeignKey('report_crontab.id', onupdate='cascade', ondelete='set null')),
        sa.Column('hash', sa.String(100)),
        sa.Column('generated', sa.DateTime),
    )

    op.create_table(
        'report_latest',
        sa.Column('portfolio_id', sa.Integer, sa.ForeignKey('portfolios.id', onupdate='cascade', ondelete='cascade'), primary_key=True),
        sa.Column('report_type_id', sa.Integer, sa.ForeignKey('report_types.id', onupdate='cascade', ondelete='cascade'), primary_key=True),
        sa.Column('report_id', sa.Integer, sa.ForeignKey('reports.id', onupdate='cascade', ondelete='set null')),
    )

    op.create_table(
        'report_crontab',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('portfolio_id', sa.Integer, sa.ForeignKey('portfolios.id', onupdate='cascade', ondelete='cascade')),
        sa.Column('report_type_id', sa.Integer, sa.ForeignKey('report_types.id', onupdate='cascade', ondelete='cascade')),
        sa.Column('cron', sa.String(300)),
        sa.Column('next_run', sa.DateTime),
        sa.Column('latest_run', sa.DateTime),
        sa.Column('latest_error', sa.Text),
        sa.Column('send_email', sa.Boolean),
    )

def downgrade():
    raise NotImplemented()
