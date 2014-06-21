from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Time, Numeric,\
    ForeignKey, event, TIMESTAMP, Date, SmallInteger, CHAR, Float
from sqlalchemy.orm import validates, relationship
from sqlalchemy.ext.declarative import declarative_base
from stocksum.web.decorators import new_session

base = declarative_base()

class User(base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), unique=True)
    email = Column(String(200), unique=True)
    created = Column(DateTime)
    timezone = Column(String(50))

class Portfolio(base):
    __tablename__ = 'portfolios'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    name = Column(String(200))
    default_currency = Column(String(10))
    created = Column(DateTime)


class Portfolio_with_transactions(Portfolio):
    transactions = relationship("Transaction", backref="parent")

def portfolio_to_dict(portfolio_id):
    with new_session() as session:
        portfolio = session.query(
            Portfolio_with_transactions
        ).filter(
            Portfolio_with_transactions.id == portfolio_id,
        ).first()
        if not portfolio:
            return None
        port = {
            'name': portfolio.name,
            'default_currency': portfolio.default_currency if portfolio.default_currency else 'DKK',
            'transactions': {},
        }
        for trans in portfolio.transactions:
            symbol = '{}:{}'.format(trans.exchange, trans.symbol) if trans.exchange else trans.symbol
            stock = port['transactions'].setdefault(symbol, [])
            stock.append({
                'shares': trans.shares,
                'paid_price': trans.paid_price,
                'trade_date': trans.trade_date,
            })
        return port

class Transaction(base):
    __tablename__ = 'transactions'
    id = Column(Integer, primary_key=True, autoincrement=True)
    portfolio_id = Column(Integer, ForeignKey('portfolios.id'))
    symbol = Column(String(20))
    exchange = Column(String(40))
    paid_price = Column(Float(precision=6))
    trade_date = Column(Date)
    shares = Column(Integer)

class Report_type(base):
    __tablename__ = 'report_types'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(60))
    description = Column(Text)
    symbol = Column(String(40), unique=True)

class Report(base):
    __tablename__ = 'reports'

    id = Column(Integer, primary_key=True, autoincrement=True)
    report_type_id = Column(Integer, ForeignKey('report_types.id'))
    portfolio_id = Column(Integer, ForeignKey('portfolios.id'))
    report_crontab_id = Column(Integer, ForeignKey('report_crontab.id'))
    hash = Column(String(100))
    generated = Column(DateTime)

class Report_latest(base):
    __tablename__ = 'report_latest'

    portfolio_id = Column(Integer, ForeignKey('report_types.id'), primary_key=True)
    report_type_id = Column(Integer, ForeignKey('report_types.id'), primary_key=True)
    report_id = Column(Integer, ForeignKey('reports.id'))

class Report_crontab(base):
    __tablename__ = 'report_crontab'

    id = Column(Integer, primary_key=True, autoincrement=True)
    portfolio_id = Column(Integer, ForeignKey('portfolios.id'))
    report_type_id = Column(Integer, ForeignKey('report_types.id'))
    cron = Column(String(300))
    next_run = Column(DateTime)
    latest_run = Column(DateTime)
    latest_error = Column(Text)
    send_email = Column(Boolean)