"""
byceps.util.datetime.format
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Date/time formatting.

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import date, datetime, time, timedelta
from typing import Optional, Union


DateOrDateTime = Union[date, datetime]


def format_custom(dt: DateOrDateTime, pattern: str) -> str:
    return dt.strftime(pattern)


def format_date_iso(d: date) -> str:
    return d.strftime('%Y-%m-%d')


def format_date_short(d: date, *, smart: bool = True) -> str:
    return (smart and _format_date_smart(d)) or d.strftime('%d.%m.%Y')


def format_date_long(d: date, *, smart: bool = True) -> str:
    return (smart and _format_date_smart(d)) or d.strftime('%A, %d. %B %Y')


def format_datetime_iso(dt: datetime) -> str:
    return dt.strftime('%Y-%m-%dT%H:%M:%S')


def format_datetime_short(dt: datetime, *, smart: bool = True) -> str:
    date_string = format_date_short(dt.date(), smart=smart)
    time_string = format_time(dt.time())

    return f'{date_string}, {time_string}'


def format_datetime_long(dt: datetime, *, smart: bool = True) -> str:
    date_string = format_date_long(dt.date(), smart=smart)
    time_string = format_time(dt.time())

    return f'{date_string}, {time_string}'


def format_time(t: time) -> str:
    return t.strftime('%H:%M Uhr')


# helpers


def _format_date_smart(d: DateOrDateTime) -> Optional[str]:
    if isinstance(d, datetime):
        d = d.date()

    today = date.today()
    if d == today:
        return 'heute'
    elif d == (today - timedelta(days=1)):
        return 'gestern'
    else:
        return None
