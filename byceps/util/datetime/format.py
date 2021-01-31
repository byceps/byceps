"""
byceps.util.datetime.format
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Date/time formatting.

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import date, datetime, time, timedelta
from typing import Optional, Union

from flask_babel import gettext


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


def format_datetime_short(
    dt: datetime, *, seconds: bool = False, smart: bool = True
) -> str:
    date_string = format_date_short(dt.date(), smart=smart)
    time_string = format_time(dt.time(), seconds=seconds)

    return f'{date_string}, {time_string}'


def format_datetime_long(
    dt: datetime, *, seconds: bool = False, smart: bool = True
) -> str:
    date_string = format_date_long(dt.date(), smart=smart)
    time_string = format_time(dt.time(), seconds=seconds)

    return f'{date_string}, {time_string}'


def format_time(t: time, seconds: bool = False) -> str:
    pattern = '%H:%M:%S Uhr' if seconds else '%H:%M Uhr'
    return t.strftime(pattern)


# helpers


def _format_date_smart(d: DateOrDateTime) -> Optional[str]:
    if isinstance(d, datetime):
        d = d.date()

    today = date.today()
    if d == today:
        return gettext('today')
    elif d == (today - timedelta(days=1)):
        return gettext('yesterday')
    else:
        return None
