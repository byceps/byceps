"""
byceps.util.datetime.monthday
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections import namedtuple

from typing_extensions import Self


class MonthDay(namedtuple('MonthDay', ['month', 'day'])):
    __slots__ = ()

    @classmethod
    def of(cls, date) -> Self:
        return cls(date.month, date.day)

    def matches(self, date):
        """Return `True` if the given date's month and day match this."""
        return self == self.__class__.of(date)
