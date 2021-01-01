"""
byceps.services.seating.transfer.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from typing import NewType
from uuid import UUID


AreaID = NewType('AreaID', UUID)


SeatID = NewType('SeatID', UUID)


SeatGroupID = NewType('SeatGroupID', UUID)


@dataclass(frozen=True)
class SeatUtilization:
    occupied: int
    total: int
