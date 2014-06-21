import json
import requests
from datetime import date, datetime

def _request(symbol):
    response = requests.get('http://www.google.com/finance/info', params={
        'q': symbol,
    })
    return response.text

def _try_float(val):
    try:
        return float(val)
    except:
        return None


def _try_date(val):
    try:
        d = [int(i) for i in val.split('/')]
        return date(
            d[2],
            d[0],
            d[1],
        )
    except:
        return None


def _format_all(value):
    return dict(
        price=_try_float(value['l_fix']),
        change=_try_float(value['c_fix']),
        transaction_exchange=value['e'],
        change_percent=_try_float(value['cp_fix']),
        symbol=value['t'],
        previous_close=_try_float(value['pcls_fix']),
    )


def get(symbol):
    '''

    :param symbol: str
        use "," to separate multiple symbols.
    :returns: list or dict
    '''
    if isinstance(symbol, list):
        symbol = ','.join(symbol) + ','
    values = json.loads(_request(
        symbol
    )[3:])
    if ',' not in symbol:
        return _format_all(values[0])
    data = {}
    for value in values:
        transaction = _format_all(value)
        data['{}:{}'.format(transaction['transaction_exchange'], transaction.pop('symbol'))] = transaction
    return data


def _request_historical_prices(symbol, period, interval=86400):
    """
    :param symbol: str
        exchange:ticker
    :param period: str
        1d = 1 day
        2y = 2 years
    :param interval: int
        prices interval
        Default is 86400 aka 1 day.
    :param returns:
    """
    params = {
        'p': period,
        'i': interval,
        'f': 'd,c,v,o,h,l',
    }
    symbol = symbol.split(':')
    if len(symbol) == 2:
        params['q'] = symbol[1]
        params['x'] = symbol[0]
    else:
        params['q'] = symbol[0]
    data = requests.get(
        'http://www.google.com/finance/getprices',
        params=params
    )
    return parse_google_get_prices(data.text)

def fill_portfolio_historical_prices(portfolio, period, interval=86400, min_fill_date=None):
    period_before_total_value = 0.0
    portfolio['period_close_value'] = 0.0
    portfolio['period_close_value_percent'] = 0.0
    for symbol in portfolio['transactions']:
        s = portfolio['transactions'][symbol]
        prices = _request_historical_prices(
            symbol=symbol,
            period=period,
            interval=interval,
        )
        close = 0.0
        close_value = 0.0
        prices_dict = {}
        if min_fill_date:
            prices = [price for price in prices if price['datetime'].date()>=min_fill_date]
        for price in prices:
            prices_dict[price['datetime'].date()] = price['close']
            close = price['close']
            close_value = price.setdefault('close_value', 0)
            close_value += sum([float(shares) * price['close'] for shares in s['shares_grouped']])
            price['close_value'] = close_value
        s['historical_prices'] = prices
        if len(prices) == 0:
            return
        s['period_close_value'] = 0.0
        for date_, shares, paid_price in zip(s['trade_dates'], s['shares_grouped'], s['paid_prices']):
            close = prices[0]['close'] if date_ not in prices_dict else paid_price
            close_value = float(shares) * close
            s['period_close_value'] += close_value
        s['period_gain'] = s['value'] - s['period_close_value']
        s['period_gain_percent'] = (s['period_gain'] / s['period_close_value']) * 100
        portfolio['period_close_value'] += s['period_close_value']
    portfolio['period_gain'] = portfolio['value'] - portfolio['period_close_value']
    portfolio['period_gain_percent'] = (portfolio['period_gain'] / portfolio['period_close_value']) * 100

def fill_portfolio_daily(portfolio):
    transactions_info = get([symbol for symbol in portfolio['transactions']])

    value = 0
    cost = 0
    gain_today = 0
    change = 0
    previous_close = 0
    price = 0

    for symbol in portfolio['transactions']:
        s = portfolio['transactions'][symbol]
        transaction_info = transactions_info[symbol]
        for transaction in s if isinstance(s, list) else [s]:
            transaction['price'] = float(transaction_info['price']) if transaction_info['price'] else float(0)

            transaction['value'] = transaction_info['price'] * transaction['shares']

            transaction['cost'] = transaction['paid_price'] * transaction['shares']
            transaction['gain'] = transaction['value'] - transaction['cost']
            transaction['gain_percent'] = (transaction['gain'] / transaction['cost']) * 100

            transaction['paid_prices'] = [transaction['paid_price']]
            transaction['trade_dates'] = [transaction['trade_date']]
            transaction['shares_grouped'] = [transaction['shares']]

            transaction['change'] = transaction_info['change'] if transaction_info['change'] else float(0)
            transaction['change_percent'] = transaction_info['change_percent'] if transaction_info['change_percent'] else float(0)
            transaction['gain_today'] = transaction_info['change'] * transaction['shares'] if transaction_info['change'] else float(0)

            transaction['previous_close'] = transaction_info['previous_close']

            value += transaction['value']
            cost += transaction['cost']
            gain_today += transaction['gain_today']
            change += transaction['change'] if transaction['change'] else 0.0
            previous_close += transaction['previous_close'] if transaction['previous_close'] else 0.0
            price += transaction_info['price']

    portfolio['value'] = value
    portfolio['cost'] = cost
    portfolio['gain'] = value - cost
    portfolio['gain_percent'] = (portfolio['gain'] / cost) * 100
    portfolio['gain_today'] = gain_today
    portfolio['change'] = change
    portfolio['change_percent'] = ((price - previous_close) / previous_close) * 100 if previous_close else 0.0
    portfolio['generated'] = datetime.utcnow()
    _fill_lots(portfolio)

def _fill_lots(portfolio):
    transactions = portfolio['transactions']
    for symbol in transactions:
        if isinstance(transactions[symbol], dict) or not transactions[symbol]:
            continue
        if len(transactions[symbol]) == 1:
            transactions[symbol] = transactions[symbol][0]
            continue
        value = 0
        cost = 0
        gain = 0
        gain_today = 0
        shares = []
        prices = []
        lots = []
        transaction = transactions[symbol][0]
        change = transaction['change']
        change_percent = transaction['change_percent']
        previous_close = transaction['previous_close']
        price = transaction['price']
        trade_date = None
        trade_dates = []
        for transaction in transactions[symbol]:
            if trade_date == None or trade_date < transaction['trade_date']:
                trade_date = transaction['trade_date']
            trade_dates.append(transaction['trade_date'])
            value += transaction['value']
            cost += transaction['cost']
            gain += transaction['gain']
            gain_today += transaction['gain_today']
            shares.append(transaction['shares'])
            prices.append(transaction['paid_price'])
            lots.append(transaction)
        paid_price = sum(prices)/float(len(prices))
        transactions[symbol] = {
            'paid_price': paid_price,
            'paid_prices': prices,
            'lots': lots,
            'lots_count': len(lots),
            'change': change,
            'change_percent': change_percent,
            'previous_close': previous_close,
            'price': price,
            'shares': sum(shares),
            'shares_grouped': shares,
            'gain': gain,
            'gain_today': gain_today,
            'gain_percent': ((value - cost) / cost) * 100,
            'value': value,
            'cost': cost,
            'trade_date': min(trade_dates),
            'trade_dates': trade_dates
        }

def parse_google_get_prices(data):
    data = data.splitlines()
    time_ = 0
    interval = int(data[3][9:])
    points = []
    for d in data[6:]:
        if d[:16] == 'TIMEZONE_OFFSET=':
            timezone_offset = int(data[6][16:])
            continue
        d = d.split(',')
        inc = 0
        if d[0][:1] == 'a':
            time_ = int(d[0][1:]) - (timezone_offset * 60)
        else:
            inc = int(d[0])
        points.append({
            'datetime': datetime.fromtimestamp(time_ + (interval * inc)),
            'close': float(d[1]),
            'high': float(d[2]),
            'low': float(d[3]),
            'open': float(d[4]),
            'volume': float(d[5]),
        })
    return points