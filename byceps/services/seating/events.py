"""
byceps.services.seating.events
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass

from byceps.services.core.events import BaseEvent
from byceps.services.seating.models import SeatGroupID
from byceps.services.ticketing.models.ticket import TicketBundleID
from byceps.services.user.models import User


@dataclass(frozen=True, kw_only=True)
class _SeatingEvent(BaseEvent):
    pass


@dataclass(frozen=True, kw_only=True)
class _SeatGroupEvent(BaseEvent):
    seat_group_id: SeatGroupID
    seat_group_title: str


@dataclass(frozen=True, kw_only=True)
class SeatGroupOccupiedEvent(_SeatGroupEvent):
    ticket_bundle_id: TicketBundleID
    ticket_bundle_owner: User


@dataclass(frozen=True, kw_only=True)
class SeatGroupReleasedEvent(_SeatGroupEvent):
    pass
