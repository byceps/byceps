# -*- coding: utf-8 -*-

"""
byceps.util.dateformat
~~~~~~~~~~~~~~~~~~~~~~

Date/time formatting.

:Copyright: 2006-2015 Jochen Kupperschmidt
"""

from datetime import date, datetime, timedelta


def register_template_filters(app):
    """Make functions available as template filters."""
    app.add_template_filter(format_custom)
    app.add_template_filter(format_date_iso)
    app.add_template_filter(format_date_short)
    app.add_template_filter(format_date_long)
    app.add_template_filter(format_datetime_iso)
    app.add_template_filter(format_datetime_short)
    app.add_template_filter(format_datetime_long)
    app.add_template_filter(format_time)


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
    return '{}, {}'.format(
        format_date_short(dt.date(), smart=smart),
        format_time(dt.time()))


def format_datetime_long(dt, *, smart=True):
    return '{}, {}'.format(
        format_date_long(dt.date(), smart=smart),
        format_time(dt.time()))


def format_time(t):
    return t.strftime('%H:%M Uhr')
