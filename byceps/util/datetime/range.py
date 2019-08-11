"""
byceps.util.datetime.range
~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from collections import namedtuple
from datetime import datetime
from typing import Iterable, Iterator

from ..iterables import pairwise


class DateTimeRange(namedtuple('DateTimeRange', ['start', 'end'])):
    """A date/time range with an inclusive start and an exclusive end."""

    __slots__ = ()

    def contains(self, datetime: datetime) -> bool:
        return self.start <= datetime < self.end

    def __repr__(self) -> str:
        return f'[{self.start}..{self.end})'


def create_adjacent_ranges(dts: Iterable[datetime]) -> Iterator[DateTimeRange]:
    """Yield adjacent ranges from successive date/time values."""
    for pair in pairwise(dts):
        yield DateTimeRange._make(pair)
