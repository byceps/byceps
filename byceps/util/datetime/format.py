# -*- coding: utf-8 -*-

"""
byceps.util.datetime.format
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Date/time formatting.

:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import date, timedelta


def format_custom(dt, pattern):
    return dt.strftime(pattern)


def format_day_smart(d):
    if hasattr(d, 'date'):
        # Seems to be a ``datetime`` object.  Convert it.
        d = d.date()

    today = date.today()
    if d == today:
        return 'heute'
    elif d == (today - timedelta(days=1)):
        return 'gestern'
    else:
        return None


def format_date_iso(d):
    return d.strftime('%Y-%m-%d')


def format_date_short(d, *, smart=True):
    return (smart and format_day_smart(d)) or d.strftime('%d.%m.%Y')


def format_date_long(d, *, smart=True):
    return (smart and format_day_smart(d)) or d.strftime('%A, %d. %B %Y')


def format_datetime_iso(dt):
    return dt.strftime('%Y-%m-%dT%H:%M:%S')


def format_datetime_short(dt, *, smart=True):
    date_string = format_date_short(dt.date(), smart=smart)
    time_string = format_time(dt.time())

    return '{}, {}'.format(date_string, time_string)


def format_datetime_long(dt, *, smart=True):
    date_string = format_date_long(dt.date(), smart=smart)
    time_string = format_time(dt.time())

    return '{}, {}'.format(date_string, time_string)


def format_time(t):
    return t.strftime('%H:%M Uhr')
