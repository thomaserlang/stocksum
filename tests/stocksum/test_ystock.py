import datetime
import calendar
import nose
from stocksum import ystock
from unittest import TestCase
from datetime import date
from mock import patch
from pprint import pprint

import time

def _request(symbol):
    return '''// [ { "id": "9835297597489" ,"t" : "TORM" ,"e" : "CPH" ,"l" : "0.925" ,"l_fix" : "0.925" ,"l_cur" : "DKK0.925" ,"s": "0" ,"ltt":"4:59PM GMT+2" ,"lt" : "Jun 4, 4:59PM GMT+2" ,"lt_dts" : "2014-06-04T16:59:35Z" ,"c" : "" ,"c_fix" : "-0.20" ,"cp" : "" ,"cp_fix" : "-0.32" ,"ccol" : "" ,"pcls_fix" : "0.925" } ,{ "id": "521441849995195" ,"t" : "VWS" ,"e" : "CPH" ,"l" : "292.80" ,"l_fix" : "292.80" ,"l_cur" : "DKK292.80" ,"s": "0" ,"ltt":"4:59PM GMT+2" ,"lt" : "Jun 4, 4:59PM GMT+2" ,"lt_dts" : "2014-06-04T16:59:43Z" ,"c" : "" ,"c_fix" : "5.10" ,"cp" : "" ,"cp_fix" : "1.77" ,"ccol" : "" ,"pcls_fix" : "287.70" } ]'''

"""
class test_ystock(TestCase):

    @patch('stocksum.ystock._request', _request)
    def test_fill_portfolio_daily(self):
        portfolio = {
            'name': 'Thomas',
            'default_currency': 'DKK',
            'transactions': {
                'CPH:VWS': {
                    'shares': 65,
                    'paid_price': 155.00,
                    'trade_date': date(2011, 5, 24),
                },
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
                ]

            }
        }

        ystock.fill_portfolio_daily(portfolio)

        result = {
            'name': 'Thomas',
            'change': 4.699999999999999,
            'change_percent': 1.7613538249007157,
            'cost': 30775.0,
            'default_currency': 'DKK',
            'gain': -11373.0,
            'gain_percent': -36.9553208773355,
            'gain_today': 251.5,
            'value': 19402.0,
            'transactions': {
                'CPH:TORM': {
                    'change': -0.2,
                    'change_percent': -0.32,
                    'cost': 20700.0,
                    'gain': -20330.0,
                    'gain_percent': -98.21256038647344,
                    'gain_today': -80.0,
                    'previous_close': 0.925,
                    'price': 0.925,
                    'paid_price': 51.75,
                    'shares': 400,
                    'value': 370.0,
                    'lots': [
                        {
                            'cost': 10600.0,
                            'gain': -10415.0,
                            'gain_percent': -98.25471698113208,
                            'gain_today': -40.0,
                            'paid_price': 53.0,
                            'shares': 200,
                            'trade_date': date(2009, 3, 4),
                            'value': 185.0
                        },
                        {
                            'cost': 10100.0,
                            'gain': -9915.0,
                            'gain_percent': -98.16831683168317,
                            'gain_today': -40.0,
                            'paid_price': 50.5,
                            'shares': 200,
                            'trade_date': date(2010, 4, 16),
                            'value': 185.0
                        }
                    ],
                    'lots_count': 2
                },
                'CPH:VWS': {
                    'change': 5.1,
                    'change_percent': 1.77,
                    'cost': 10075.0,
                    'gain': 8957.0,
                    'gain_percent': 88.90322580645162,
                    'gain_today': 331.5,
                    'previous_close': 287.7,
                    'price': 292.8,
                    'paid_price': 155.0,
                    'shares': 65,
                    'trade_date': date(2011, 5, 24),
                    'value': 19032.0
                }
            }
        }

        self.assertEqual(portfolio, result)
"""
class Test_parse_google_get_prices(TestCase):
    def test_parse_google_get_prices(self):

        points = ystock.parse_google_get_prices(
'''EXCHANGE%3DCPH
MARKET_OPEN_MINUTE=540
MARKET_CLOSE_MINUTE=1020
INTERVAL=86400
COLUMNS=DATE,CLOSE,HIGH,LOW,OPEN,VOLUME
DATA=
TIMEZONE_OFFSET=120
a1402412400,294.2,303,292.2,300.1,2876018
1,288.2,297.8,286.2,296.1,2683510
TIMEZONE_OFFSET=60
a1402412700,294.2,303,292.2,300.1,2876018
3,288.2,297.8,286.2,296.1,2683510
'''
        )
        self.assertEqual(
            points,
            [{'volume': 2876018.0, 'datetime': datetime.datetime(2014, 6, 10, 15, 0), 'high': 303.0, 'low': 292.2, 'close': 294.2, 'open': 300.1}, {'volume': 2683510.0, 'datetime': datetime.datetime(2014, 6, 11, 15, 0), 'high': 297.8, 'low': 286.2, 'close': 288.2, 'open': 296.1}, {'volume': 2876018.0, 'datetime': datetime.datetime(2014, 6, 10, 15, 5), 'high': 303.0, 'low': 292.2, 'close': 294.2, 'open': 300.1}, {'volume': 2683510.0, 'datetime': datetime.datetime(2014, 6, 13, 15, 5), 'high': 297.8, 'low': 286.2, 'close': 288.2, 'open': 296.1}]
        )


if __name__ == '__main__':
    nose.run(defaultTest=__name__)