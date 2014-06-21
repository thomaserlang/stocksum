"""add portfolio table

Revision ID: 1c9398290e4
Revises: 3c4f298b063
Create Date: 2014-05-31 21:43:26.498832

"""

# revision identifiers, used by Alembic.
revision = '1c9398290e4'
down_revision = '3c4f298b063'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'portfolios',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id', onupdate='cascade', ondelete='cascade')),
        sa.Column('name', sa.String(200)),
        sa.Column('created', sa.DateTime),
        sa.Column('default_currency', sa.String(10))
    )

    op.create_table(
        'transactions',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('portfolio_id', sa.Integer, sa.ForeignKey('portfolios.id', onupdate='cascade', ondelete='cascade')),
        sa.Column('symbol', sa.String(20)),
        sa.Column('exchange', sa.String(40)),
        sa.Column('paid_price', sa.Float(precision=6)),
        sa.Column('trade_date', sa.Date),
        sa.Column('shares', sa.Integer),
    )


def downgrade():
    raise NotImplemented()
