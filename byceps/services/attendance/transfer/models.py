"""
byceps.services.attendance.transfer.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from dataclasses import dataclass

from ....services.seating.models.seat import Seat
from ....services.user.models.user import User


@dataclass  # Not yet frozen b/c models are not immutable.
class Attendee:
    user: User
    seat: Seat
    checked_in: bool
