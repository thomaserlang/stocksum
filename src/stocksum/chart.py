import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import io
from matplotlib.dates import date2num, YearLocator, MonthLocator, DayLocator,\
    DateFormatter, WeekdayLocator, MO, HourLocator
from matplotlib.ticker import FuncFormatter
from collections import OrderedDict

def _group_by_datetime(portfolio):
    data = OrderedDict()
    for symbol in portfolio['transactions']:
        s = portfolio['transactions'][symbol]
        for hist in s['historical_prices']:
            d = data.setdefault(hist['datetime'], 0)
            d += hist['close_value']
            data[hist['datetime']] = d

    dates = [d for d in data]
    close = [data[d] for d in data]
    return (dates, close)

def _get_chart(major_locator, major_formatter, minor_locator,
               date_group_formatter, dates, close, currency,
               line_format='b.-'):
    #plt.ion()
    #plt.clf()

    fig, ax = plt.subplots()
    ax.plot_date(
        date2num(dates),
        close,
        line_format,
    )
    ax.fill_between(
        dates,
        min(close),
        close,
        facecolor='blue',
        alpha=0.2
    )
    ax.xaxis.set_major_locator(major_locator)
    ax.xaxis.set_major_formatter(major_formatter)
    ax.xaxis.set_minor_locator(minor_locator)

    ax.autoscale_view()
    #ax.set_xlim(dates[0], dates[len(dates)-1])

    def price(x):
        return '{:.2f}'.format(x)
    def fmy(x, pos):
        return '{:,.0f} {}'.format(x, currency)
    ax.fmt_xdata = DateFormatter(date_group_formatter)
    ax.fmt_ydata = price
    ax.yaxis.set_major_formatter(FuncFormatter(fmy))
    ax.grid(True)

    fig.autofmt_xdate()
    ax.set_title('Portfolio value')
    fig.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    return buf

def get_daily_chart(portfolio):
    dates, close = _group_by_datetime(portfolio)
    return _get_chart(
        major_locator=HourLocator(),
        major_formatter=DateFormatter('%H'),
        minor_locator=HourLocator(),
        date_group_formatter='%H',
        dates=dates,
        close=close,
        currency=portfolio['default_currency'],
    )

def get_weekly_chart(portfolio):
    dates, close = _group_by_datetime(portfolio)
    return _get_chart(
        major_locator=DayLocator(),
        major_formatter=DateFormatter('%A'),
        minor_locator=DayLocator(),
        date_group_formatter='%d',
        dates=dates,
        close=close,
        currency=portfolio['default_currency'],
    )

def get_monthly_chart(portfolio):
    dates, close = _group_by_datetime(portfolio)
    return _get_chart(
        major_locator=WeekdayLocator(byweekday=MO),
        major_formatter=DateFormatter('%d. %b'),
        minor_locator=DayLocator(),
        date_group_formatter='%Y-%m-%d',
        dates=dates,
        close=close,
        currency=portfolio['default_currency'],
    )

def get_yearly_chart(portfolio):
    dates, close = _group_by_datetime(portfolio)
    return _get_chart(
        major_locator=MonthLocator(),
        major_formatter=DateFormatter('%b'),
        minor_locator=MonthLocator(),
        date_group_formatter='%Y-%m-%d',
        dates=dates,
        close=close,
        currency=portfolio['default_currency'],
        line_format='-'
    )