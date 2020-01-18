"""
byceps.util.datetime.monthday
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from collections import namedtuple


class MonthDay(namedtuple('MonthDay', ['month', 'day'])):

    __slots__ = ()

    @classmethod
    def of(cls, date):
        return cls(date.month, date.day)

    def matches(self, date):
        """Return `True` if the given date's month and day match this."""
        return self == self.__class__.of(date)
