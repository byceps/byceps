"""
byceps.services.attendance.transfer.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from attr import attrib, attrs

from ....services.seating.models.seat import Seat
from ....services.user.models.user import User


@attrs(slots=True)  # Not yet frozen b/c models are not immutable.
class Attendee:
    user = attrib(type=User)
    seat = attrib(type=Seat)
    checked_in = attrib(type=bool)
