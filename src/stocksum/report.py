import time
import croniter
import hashlib
import os, os.path
import logging
import pytz
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor
from stocksum.config import config
from stocksum.web.decorators import new_session
from stocksum.web import models, utils
from datetime import datetime, date
from stocksum import template, ystock, mail, chart
from stocksum.logger import Logger

def generate_report(crontab_id):
    try:
        with new_session() as session:
            session.query(
                models.Report_crontab,
            ).filter(
                models.Report_crontab.id == crontab_id,
            ).update({
                'next_run': None,
            })
            session.commit()
            cron = session.query(
                models.Report_crontab,
                models.Report_type,
            ).filter(
                models.Report_crontab.id == crontab_id,
                models.Report_type.id == models.Report_crontab.report_type_id,
            ).first()
            portfolio = models.portfolio_to_dict(cron.Report_crontab.portfolio_id)
            user = session.query(
                models.User,
            ).filter(
                models.Portfolio.id == cron.Report_crontab.portfolio_id,
                models.User.id == models.Portfolio.user_id,
            ).first()
            if not user:
                raise Exception('no user found for portfolio id: {}'.format(cron.Report_crontab.portfolio_id))
            try:
                hash_ = None
                if cron.Report_type.symbol == 'daily':
                    hash_ = generate_report_daily(cron, portfolio, user)
                elif cron.Report_type.symbol in (
                        '1-week',
                        '1-month',
                        '3-months',
                        '6-months',
                        '1-year',
                        'ytd',
                    ):
                    hash_ = generate_period_report(
                        cron=cron,
                        portfolio=portfolio,
                        user=user,
                        report_type_symbol=cron.Report_type.symbol,
                    )
                if hash_:
                    report = models.Report(
                        report_type_id=cron.Report_type.id,
                        portfolio_id=cron.Report_crontab.portfolio_id,
                        report_crontab_id=crontab_id,
                        hash=hash_,
                        generated=portfolio['generated'],
                    )
                    session.add(report)
                    session.flush()
                    report_latest = models.Report_latest(
                        portfolio_id=cron.Report_crontab.portfolio_id,
                        report_type_id=cron.Report_type.id,
                        report_id=report.id,
                    )
                    session.merge(report_latest)
            except:
                logging.exception('Report generation failed for crontab id: {}'.format(crontab_id))
            cron.Report_crontab.latest_run = datetime.utcnow()
            __cron = croniter.croniter(
                cron.Report_crontab.cron,
                datetime.astimezone(
                    datetime.utcnow().replace(tzinfo=pytz.utc),
                    pytz.timezone(user.timezone),
                ).replace(tzinfo=None)
            )
            next_ = __cron.get_next(datetime)
            tz = pytz.timezone(user.timezone)
            next_ = tz.localize(next_)
            next_ = next_.astimezone(pytz.utc)
            cron.Report_crontab.next_run = next_
            session.commit()
    except:
        logging.exception('Report generation failed for crontab id: {}'.format(crontab_id))


def generate_report_daily(cron, portfolio, user):
    ystock.fill_portfolio_daily(portfolio)
    html = template.daily_template(portfolio, user)
    date_ = datetime.utcnow().strftime('%Y%m%d')
    hash_ = '{}/{}'.format(
        date_,
        hashlib.sha1(html.encode('utf-8')).hexdigest(),
    )
    path = os.path.join(config['report']['path'], hash_)

    date_path = os.path.join(config['report']['path'], date_)
    if not os.path.exists(date_path):
        os.makedirs(date_path)
    with open(path+'.html', r'wb') as f:
        f.write(html.encode('utf-8'))
    with open(path+'.json', r'wb') as f:
        f.write(
            utils.json_dumps(
                portfolio,
                sort_keys=True,
                indent=4,
                separators=(',', ': '),
            ).encode('utf-8'),
        )
    subject = 'Stocksum - {} report: {} {:+,.2f} ({:.2f}%) gained today'.format(
        cron.Report_type.name,
        portfolio['default_currency'],
        portfolio['gain_today'],
        portfolio['change_percent'],
    )
    if cron.Report_crontab.send_email:
        mail.Mail.send(
            [user.email],
            subject,
            template.daily_email_template(
                portfolio,
                urljoin(config['web']['base_url'], 'reports/{}.html'.format(hash_)),
            ),
            from_base=cron.Report_type.symbol,
        )
    return hash_

def generate_period_report(cron, portfolio, user, report_type_symbol):
    ystock.fill_portfolio_daily(portfolio)
    periods = {
        '1-week': '5d',
        '1-month': '20d',
        '3-months': '3M',
        '6-months': '6M',
        '1-year': '1Y',
        'ytd': '1Y',
    }
    ystock.fill_portfolio_historical_prices(
        portfolio,
        periods[report_type_symbol],
        min_fill_date=date(date.today().year, 1, 1) if report_type_symbol == 'ytd' else None,
    )

    attachments = []
    if report_type_symbol == '1-week':
        attachments.append(chart.get_weekly_chart(portfolio))
    elif 'months' in report_type_symbol:
        attachments.append(chart.get_yearly_chart(portfolio))
    elif '1-month' == report_type_symbol:
        attachments.append(chart.get_monthly_chart(portfolio))
    elif '1-year' == report_type_symbol:
        attachments.append(chart.get_yearly_chart(portfolio))
    elif 'ytd' == report_type_symbol:
        attachments.append(chart.get_yearly_chart(portfolio))
    html = template.period_template(
        portfolio,
        user,
        period_name=report_type_symbol,
        images=attachments,
    )
    date_ = datetime.utcnow().strftime('%Y%m%d')
    hash_ = '{}/{}'.format(
        date_,
        hashlib.sha1(html.encode('utf-8')).hexdigest(),
    )
    path = os.path.join(config['report']['path'], hash_)

    date_path = os.path.join(config['report']['path'], date_)
    if not os.path.exists(date_path):
        os.makedirs(date_path)
    with open(path+'.html', r'wb') as f:
        f.write(html.encode('utf-8'))
    with open(path+'.json', r'wb') as f:
        f.write(
            utils.json_dumps(
                portfolio,
                sort_keys=True,
                indent=4,
                separators=(',', ': '),
            ).encode('utf-8'),
        )
    subject = 'Stocksum - {} report: {} {:+,.2f} gain'.format(
        cron.Report_type.name,
        portfolio['default_currency'],
        portfolio['period_close_value'],
        portfolio['period_close_value_percent'],
    )
    if cron.Report_crontab.send_email:
        mail.Mail.send(
            [user.email],
            subject,
            template.period_email_template(
                portfolio,
                urljoin(config['web']['base_url'], 'reports/{}.html'.format(hash_)),
                period_name=report_type_symbol,
            ),
            from_base=cron.Report_type.symbol,
            attachments=attachments,
        )

    return hash_

def main():
    Logger.set_logger('report.log')
    try:
        executor = ThreadPoolExecutor(max_workers=config['report']['max_workers'])
        with new_session() as session:
            while True:
                try:
                    crontab = session.query(
                        models.Report_crontab,
                    ).filter(
                        models.Report_crontab.next_run <= datetime.utcnow(),
                    ).all()
                    for cron in crontab:
                        executor.submit(generate_report, cron.id)
                    time.sleep(5)
                except Exception as e:
                    if isinstance(e, KeyboardInterrupt):
                        raise
                    logging.exception('Report main loop exception')
    except:
        logging.exception('Report startup exception')

if __name__ == '__main__':
    main()