"""
byceps.blueprints.ticketing_admin.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import Iterator

from ...services.ticketing import event_service
from ...services.ticketing.models.ticket import TicketID
from ...services.ticketing.models.ticket_event import TicketEventData


def get_events(ticket_id: TicketID) -> Iterator[TicketEventData]:
    events = event_service.get_events_for_ticket(ticket_id)

    for event in events:
        yield {
            'event': event.event_type,
            'occured_at': event.occured_at,
            'data': event.data,
        }
