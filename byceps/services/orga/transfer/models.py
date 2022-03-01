"""
byceps.services.orga.transfer.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from datetime import date
from typing import Optional

from ....util.datetime.calc import calculate_age, calculate_days_until
from ....util.datetime.monthday import MonthDay


@dataclass(frozen=True)
class Birthday:
    date_of_birth: date

    @property
    def age(self) -> Optional[int]:
        """Return the current age."""
        return calculate_age(self.date_of_birth, today())

    @property
    def days_until_next_birthday(self) -> Optional[int]:
        """Return the number of days until the next birthday."""
        return calculate_days_until(self.date_of_birth, today())

    @property
    def is_today(self) -> Optional[bool]:
        """Return `True` if the birthday is today."""
        return MonthDay.of(self.date_of_birth).matches(today())


def today() -> date:
    return date.today()
