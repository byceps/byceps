"""
byceps.services.seating.events
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass

from byceps.services.core.events import _BaseEvent, EventUser
from byceps.services.seating.models import SeatGroupID
from byceps.services.ticketing.models.ticket import TicketBundleID


@dataclass(frozen=True, kw_only=True)
class _SeatingEvent(_BaseEvent):
    pass


@dataclass(frozen=True, kw_only=True)
class _SeatGroupEvent(_BaseEvent):
    seat_group_id: SeatGroupID
    seat_group_title: str


@dataclass(frozen=True, kw_only=True)
class SeatGroupOccupiedEvent(_SeatGroupEvent):
    ticket_bundle_id: TicketBundleID
    ticket_bundle_owner: EventUser


@dataclass(frozen=True, kw_only=True)
class SeatGroupReleasedEvent(_SeatGroupEvent):
    pass
