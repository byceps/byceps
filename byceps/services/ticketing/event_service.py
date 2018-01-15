"""
byceps.services.ticketing.event_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime
from typing import Sequence

from ...database import db

from .models.ticket import TicketID
from .models.ticket_event import TicketEvent, TicketEventData


def create_event(event_type: str, ticket_id: TicketID, data: TicketEventData
                ) -> None:
    """Create a ticket event."""
    event = _build_event(event_type, ticket_id, data)

    db.session.add(event)
    db.session.commit()


def _build_event(event_type: str, ticket_id: TicketID, data: TicketEventData
                ) -> TicketEvent:
    """Assemble, but not persist, a ticket event."""
    now = datetime.utcnow()

    return TicketEvent(now, event_type, ticket_id, data)


def get_events_for_ticket(ticket_id: TicketID) -> Sequence[TicketEvent]:
    """Return the events for that ticket."""
    return TicketEvent.query \
        .filter_by(ticket_id=ticket_id) \
        .order_by(TicketEvent.occurred_at) \
        .all()
