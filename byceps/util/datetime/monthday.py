"""
byceps.util.datetime.monthday
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import NamedTuple, Self


class MonthDay(NamedTuple):
    month: int
    day: int

    @classmethod
    def of(cls, date) -> Self:
        return cls(date.month, date.day)

    def matches(self, date):
        """Return `True` if the given date's month and day match this."""
        return self == self.__class__.of(date)
