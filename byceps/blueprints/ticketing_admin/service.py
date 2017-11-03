"""
byceps.blueprints.ticketing_admin.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import Iterator

from ...services.ticketing import event_service
from ...services.ticketing.models.ticket import TicketID
from ...services.ticketing.models.ticket_event import TicketEvent, \
    TicketEventData
from ...services.ticketing import ticket_service


def get_events(ticket_id: TicketID) -> Iterator[TicketEventData]:
    events = event_service.get_events_for_ticket(ticket_id)
    events.insert(0, _fake_ticket_creation_event(ticket_id))

    for event in events:
        yield {
            'event': event.event_type,
            'occurred_at': event.occurred_at,
            'data': event.data,
        }


def _fake_ticket_creation_event(ticket_id: TicketID) -> TicketEvent:
    ticket = ticket_service.find_ticket(ticket_id)
    if ticket is None:
        raise ValueError('Unknown ticket ID')

    data = {}

    return TicketEvent(ticket.created_at, 'ticket-created', ticket.id, data)
