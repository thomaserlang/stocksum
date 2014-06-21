import ystock
import pytz
import base64
from mail import Mail
from datetime import date
from jinja2 import FileSystemLoader
from jinja2.environment import Environment
from pprint import pprint
from datetime import datetime, date
from stocksum import chart

env = Environment()
env.loader = FileSystemLoader('./templates')

def get_transaction_number_color(number):
    if number > 0:
        return '#339933'
    elif number < 0:
        return '#FF0000'
    return '#000000'

def get_transaction_number_symbol(number):
    if number > 0:
        return '+'
    return '#000000'

def format_transaction_number(number, percent=None, add_color=True):
    if not add_color:
        return '<font>{:,.2f}</font>'.format(number)
    color = get_transaction_number_color(number)
    if percent == None:
        return '<font color="{}">{:+,.2f}</font>'.format(
            color,
            number,
        )
    return '<font color="{}">{:+,.2f} ({:.2f}%)</font>'.format(
        color,
        number,
        percent,
    )

def daily_template(portfolio, user=None):
    '''
    :returns: str
        A HTML formattet document.
    '''
    tmpl = env.get_template('daily_report.html')

    html = tmpl.render(
        sorted_symbols=sorted(portfolio['transactions'], key=lambda key: portfolio['transactions'][key]['change_percent'], reverse=True),
        portfolio=portfolio,
        fm=format_transaction_number,
        user_time=user_time,
        user=user,
    )
    return html

def period_template(portfolio, user=None, period_name='', images=[]):
    '''
    :returns: str
        A HTML formattet document.
    '''
    tmpl = env.get_template('period_report.html')

    html = tmpl.render(
        sorted_symbols=sorted(portfolio['transactions'], key=lambda key: portfolio['transactions'][key]['change_percent'], reverse=True),
        portfolio=portfolio,
        fm=format_transaction_number,
        user_time=user_time,
        user=user,
        period_name=period_name,
        images=images,
        base64=base64.b64encode,
    )
    return html

def user_time(user, dt=None):
    if not dt:
        dt = datetime.utcnow()
    return datetime.astimezone(
        dt.replace(tzinfo=pytz.utc),
        pytz.timezone(user.timezone),
    )

def daily_email_template(portfolio, url=None):
    '''
    :param portfolio: dict
    :param url: str
        url to a HTML version.
    :returns: str
        A HTML formattet document ready to send by email.
    '''
    tmpl = env.get_template('daily_email_report.html')

    html = tmpl.render(
        sorted_symbols=sorted(portfolio['transactions'], key=lambda key: portfolio['transactions'][key]['change_percent'], reverse=True),
        portfolio=portfolio,
        fm=format_transaction_number,
        url=url,
    )
    return html

def period_email_template(portfolio, url=None, period_name=''):
    '''
    :param portfolio: dict
    :param url: str
        url to a HTML version.
    :returns: str
        A HTML formattet document ready to send by email.
    '''
    tmpl = env.get_template('period_email_report.html')

    html = tmpl.render(
        sorted_symbols=sorted(portfolio['transactions'], key=lambda key: portfolio['transactions'][key]['change_percent'], reverse=True),
        portfolio=portfolio,
        fm=format_transaction_number,
        url=url,
        period_name=period_name,
    )
    return html

if __name__ == '__main__':
    portfolio = {
        'name': 'Thomas',
        'default_currency': 'DKK',
        'transactions': {
            'CPH:VWS': [
                {
                    'shares': 65,
                    'paid_price': 155.00,
                    'trade_date': date(2011, 5, 24),
                }
            ],
            'CPH:TORM': [
                {
                    'shares': 200,
                    'paid_price': 53.00,
                    'trade_date': date(2009, 3, 4),
                },
                {
                    'shares': 200,
                    'paid_price': 50.50,
                    'trade_date': date(2010, 4, 16),
                },
            ],
            'CPH:ALK-B': {
                'shares': 15,
                'paid_price': 815.00,
                'trade_date': date(2014, 5, 19),
            },
            'CPH:DSV': {
                'shares': 60,
                'paid_price': 168.80,
                'trade_date': date(2014, 2, 17),
            },
            'CPH:LUN': {
                'shares': 70,
                'paid_price': 154.90,
                'trade_date': date(2014, 5, 19),
            },
            'CPH:MAERSK-B': {
                'shares': 1,
                'paid_price': 12810.00,
                'trade_date': date(2014, 4, 7),
            },
            'CPH:PNDORA': [
                {
                    'shares': 31,
                    'paid_price': 324.10,
                    'trade_date': date(2014, 2, 17),
                },
                {
                    'shares': 30,
                    'paid_price': 356.00,
                    'trade_date': date(2014, 3, 3),
                },
            ],
            'CPH:ROCK-B': {
                'shares': 10,
                'paid_price': 1080.00,
                'trade_date': date(2014, 5, 19),
            },
        }
    }
    ystock.fill_portfolio_daily(portfolio)
    ystock.fill_portfolio_historical_prices(
        portfolio,
        '1M'
    )
    buf = chart.get_yearly_chart(portfolio)
    with open('chart.png', 'wb+') as fd:
        buf.seek(0)
        t = buf.read(1048576)
        while t:
          fd.write(t)
          t = buf.read(1048576)