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

    def matches(self, date):
        """Return `True` if the given date's month and day match this."""
        return self == self.__class__.of(date)


def calculate_age(date_of_birth, today):
    """Calculate the number of full years since the date of birth until
    today.
    """
    age = today.year - date_of_birth.year
    if MonthDay.of(date_of_birth) > MonthDay.of(today):
        age -= 1
    return age


def calculate_days_until(date, today):
    """Calculate the number of days from today until the given date."""
    date_this_year = date.replace(year=today.year)
    if date_this_year < today:
        date_this_year = date.replace(year=date_this_year.year + 1)

    delta = date_this_year - today
    return delta.days
