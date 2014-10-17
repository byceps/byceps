# -*- coding: utf-8 -*-

"""
byceps.util.datetime
~~~~~~~~~~~~~~~~~~~~

Date/time supplements.

:Copyright: 2006-2014 Jochen Kupperschmidt
"""

from collections import namedtuple


class MonthDay(namedtuple('MonthDay', ['month', 'day'])):

    @classmethod
    def of(cls, date):
        return cls(date.month, date.day)


def calculate_days_until(date, today):
    """Calculate the number of days until the given date."""
    date_this_year = date.replace(year=today.year)
    if date_this_year < today:
        date_this_year = date.replace(year=date_this_year.year + 1)

    delta = date_this_year - today
    return delta.days
