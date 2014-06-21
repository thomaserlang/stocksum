import logging
import time
import croniter
import pytz
from tornado.web import authenticated, HTTPError
from stocksum.web.handlers import base
from stocksum.config import config
from stocksum.web import models, utils, decorators
from stocksum.web.decorators import new_session
from datetime import datetime, date

class Handler(base.Handler):

    @authenticated
    def get(self):
        with new_session() as session:
            if not self.get_argument('id', None):
                portfolio = session.query(models.Portfolio).filter(
                    models.Portfolio.user_id == self.current_user['id']
                 ).first()
                if portfolio:
                    self.redirect('/portfolios?id={}'.format(portfolio.id))
                    return
            else:
                portfolio = session.query(models.Portfolio).filter(
                    models.Portfolio.user_id == self.current_user['id'],
                    models.Portfolio.id == self.get_argument('id'),
                 ).first()
                if not portfolio:
                    raise HTTPError(404, 'Unknown portfolio!')
            self.render('portfolios.html',
                portfolio=portfolio,
            )

class API_handler(base.API_handler):

    @authenticated
    def post(self):
        name = self.get_argument('name')
        with new_session() as session:
            portfolio = models.Portfolio(
                name=name[:200],
                user_id=self.current_user['id'],
                created=datetime.utcnow(),
            )
            session.add(portfolio)
            session.commit()
            self.write_object({
                'id': portfolio.id,
            })

class Edit_transactions_handler(base.Handler):

    @authenticated
    def get(self):
        with new_session() as session:
            portfolio = session.query(models.Portfolio).filter(
                models.Portfolio.user_id == self.current_user['id'],
                models.Portfolio.id == self.get_argument('id'),
             ).first()
            if not portfolio:
                raise HTTPError(404, 'Unknown portfolio!')
            transactions = session.query(models.Transaction).filter(
                models.Transaction.portfolio_id == self.get_argument('id'),
            ).all()
            self.render('portfolio_edit.html',
                portfolio=portfolio,
                transactions=transactions if transactions else [],
            )

    @authenticated
    def post(self):
        with new_session() as session:
            transactions = zip(
                self.get_arguments('symbol'),
                self.get_arguments('trade_date'),
                self.get_arguments('shares'),
                self.get_arguments('paid_price'),
                self.get_arguments('index'),
            )
            id_ = self.get_argument('id')
            session.query(models.Transaction).filter(
                models.Transaction.portfolio_id == id_
            ).delete()
            for symbol, trade_date, shares, paid_price, index in transactions:
                if self.get_argument('delete-{}'.format(index), None):
                    continue
                symbol_arr = symbol.split(':')
                if len(symbol_arr) != 2:
                    symbol_arr = ['', symbol]
                transaction = models.Transaction(
                    portfolio_id=id_,
                    symbol=symbol_arr[1],
                    exchange=symbol_arr[0],
                    trade_date=datetime.strptime(trade_date, '%Y-%m-%d'),
                    shares=shares,
                    paid_price=paid_price,
                )
                session.add(transaction)
            session.commit()
            self.write({'status': 'OK'})

class Edit_crontab_handler(base.Handler):

    @authenticated
    def get(self):
        id_ = self.get_argument('id')
        with new_session() as session:
            report_types = session.query(
                models.Report_type
            ).order_by(
                models.Report_type.id,
            ).all()
            crontab = session.query(
                models.Report_crontab,
            ).filter(
                models.Report_crontab.portfolio_id == id_
            ).order_by(
                models.Report_crontab.id,
            ).all()
            self.render('portfolio_edit_report_cron.html',
                report_types=report_types,
                crontab=crontab,
                portfolio_id=id_,
            )

    @authenticated
    def post(self):
        id_ = self.get_argument('id')
        with new_session() as session:
            portfolio = session.query(models.Portfolio).filter(
                models.Portfolio.user_id == self.current_user['id'],
                models.Portfolio.id == id_,
            ).first()
            if not portfolio:
                self.set_status(403)
                self.write({
                    'error': 'this is not your portfolio'
                })
                return
            crontab = zip(
                self.get_arguments('cron_id'),
                self.get_arguments('report_type_id'),
                self.get_arguments('cron'),
            )
            for cron_id, report_type_id, cron in crontab:
                try:
                    __cron = croniter.croniter(
                        cron,
                        self.user_time().replace(tzinfo=None),
                    )
                except (KeyError, ValueError):
                    self.set_status(400)
                    self.write({
                        'error': 'wrong cron format'
                    })
                    return
                query = session.query(
                    models.Report_crontab
                ).filter(
                    models.Report_crontab.id == cron_id,
                    models.Report_crontab.portfolio_id == id_,
                )
                if self.get_argument('delete-{}'.format(cron_id), None):
                    query.delete()
                else:
                    next_ = __cron.get_next(datetime)
                    tz = pytz.timezone(self.current_user['timezone'])
                    next_ = tz.localize(next_)
                    next_ = next_.astimezone(pytz.utc)
                    query.update({
                        'report_type_id': report_type_id,
                        'cron': cron,
                        'next_run': next_,
                        'send_email': True if self.get_argument('send-email-{}'.format(cron_id), False) == 'true' else False,
                    })
            session.commit()

class New_cron_handler(base.Handler):

    @authenticated
    def post(self):
        id_ = self.get_argument('id')
        cron = self.get_argument('cron')
        with new_session() as session:
            portfolio = session.query(models.Portfolio).filter(
                models.Portfolio.user_id == self.current_user['id'],
                models.Portfolio.id == id_,
            ).first()
            if not portfolio:
                self.set_status(403)
                self.write({
                    'error': 'this is not your portfolio'
                })
                return
            try:
                __cron = croniter.croniter(
                    cron,
                    self.user_time().replace(tzinfo=None),
                )
            except (KeyError, ValueError):
                self.set_status(400)
                self.write({
                    'error': 'wrong cron format'
                })
                return

            next_ = __cron.get_next(datetime)
            tz = pytz.timezone(self.current_user['timezone'])
            next_ = tz.localize(next_)
            next_ = next_.astimezone(pytz.utc)
            cron = models.Report_crontab(
                portfolio_id=id_,
                report_type_id=self.get_argument('report_type_id'),
                cron=cron,
                next_run=next_,
                send_email=True if self.get_argument('send-email', False) == 'true' else False,
            )
            session.add(cron)
            session.commit()
        self.write({'status': 'OK'})