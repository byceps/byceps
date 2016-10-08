# -*- coding: utf-8 -*-

"""
byceps.util.datetime
~~~~~~~~~~~~~~~~~~~~

Date/time supplements.

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from collections import namedtuple


class DateTimeRange(namedtuple('DateTimeRange', ['start', 'end'])):
    """A date/time range with an inclusive start and an exclusive end."""

    __slots__ = ()

    def contains(self, datetime):
        return self.start <= datetime < self.end

    def __repr__(self):
        return '[{0.start}..{0.end})'.format(self)


class MonthDay(namedtuple('MonthDay', ['month', 'day'])):

    __slots__ = ()

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
