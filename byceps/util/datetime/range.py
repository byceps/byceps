"""
byceps.util.datetime.range
~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, Iterator

from ..iterables import pairwise


@dataclass(frozen=True)
class DateTimeRange:
    """A date/time range with an inclusive start and an exclusive end."""

    start: datetime
    end: datetime

    def contains(self, dt: datetime) -> bool:
        return self.start <= dt < self.end

    def __contains__(self, dt: datetime) -> bool:
        """Return `True` if the date/time is contained in the range
        represented by this object.
        """
        return self.contains(dt)

    def __repr__(self) -> str:
        return f'[{self.start}..{self.end})'


def create_adjacent_ranges(dts: Iterable[datetime]) -> Iterator[DateTimeRange]:
    """Yield adjacent ranges from successive date/time values."""
    for start, end in pairwise(dts):
        yield DateTimeRange(start, end)
