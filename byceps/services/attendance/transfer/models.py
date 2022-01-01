"""
byceps.services.attendance.transfer.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

from ....services.seating.dbmodels.seat import Seat
from ....services.user.dbmodels.user import User


@dataclass  # Not yet frozen b/c models are not immutable.
class AttendeeTicket:
    seat: Optional[Seat]
    checked_in: bool


@dataclass  # Not yet frozen b/c models are not immutable.
class Attendee:
    user: User
    tickets: list[AttendeeTicket]
