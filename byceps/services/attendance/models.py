"""
byceps.services.attendance.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from typing import Optional

from byceps.services.seating.dbmodels.seat import DbSeat
from byceps.services.user.dbmodels.user import DbUser


@dataclass  # Not yet frozen b/c models are not immutable.
class AttendeeTicket:
    seat: Optional[DbSeat]
    checked_in: bool


@dataclass  # Not yet frozen b/c models are not immutable.
class Attendee:
    user: DbUser
    tickets: list[AttendeeTicket]
