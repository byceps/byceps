"""
byceps.services.ticketing.event_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime
from typing import List

from ...database import db

from .dbmodels.ticket_event import TicketEvent, TicketEventData
from .transfer.models import TicketID


def create_event(
    event_type: str, ticket_id: TicketID, data: TicketEventData
) -> None:
    """Create a ticket event."""
    event = build_event(event_type, ticket_id, data)

    db.session.add(event)
    db.session.commit()


def build_event(
    event_type: str, ticket_id: TicketID, data: TicketEventData
) -> TicketEvent:
    """Assemble, but not persist, a ticket event."""
    now = datetime.utcnow()

    return TicketEvent(now, event_type, ticket_id, data)


def get_events_for_ticket(ticket_id: TicketID) -> List[TicketEvent]:
    """Return the events for that ticket."""
    return TicketEvent.query \
        .filter_by(ticket_id=ticket_id) \
        .order_by(TicketEvent.occurred_at) \
        .all()
