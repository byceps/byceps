"""
byceps.blueprints.ticketing_admin.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import Any, Dict, Iterator, Tuple

from ...services.seating import seat_service
from ...services.ticketing import event_service
from ...services.ticketing.models.ticket import TicketID
from ...services.ticketing.models.ticket_event import TicketEvent, \
    TicketEventData
from ...services.ticketing import ticket_service
from ...services.user.models.user import User, UserTuple
from ...services.user import service as user_service
from ...typing import UserID


def get_events(ticket_id: TicketID) -> Iterator[TicketEventData]:
    events = event_service.get_events_for_ticket(ticket_id)
    events.insert(0, _fake_ticket_creation_event(ticket_id))

    user_ids = {event.data['initiator_id']
                for event in events
                if 'initiator_id' in event.data}
    users = user_service.find_users(user_ids)
    users_by_id = {str(user.id): user for user in users}

    for event in events:
        data = {
            'event': event.event_type,
            'occurred_at': event.occurred_at,
            'data': event.data,
        }

        data.update(_get_additional_data(event, users_by_id))

        yield data


def _fake_ticket_creation_event(ticket_id: TicketID) -> TicketEvent:
    ticket = ticket_service.find_ticket(ticket_id)
    if ticket is None:
        raise ValueError('Unknown ticket ID')

    data = {}

    return TicketEvent(ticket.created_at, 'ticket-created', ticket.id, data)


def _get_additional_data(event: TicketEvent,
                         users_by_id: Dict[UserID, UserTuple]
                        ) -> Iterator[Tuple[str, Any]]:
    if event.event_type in {
            'seat-occupied',
            'seat-released',
            'ticket-revoked',
    }:
        yield from _get_additional_data_for_user_initiated_event(event,
                                                                 users_by_id)

    if event.event_type == 'seat-occupied':
        yield from _get_additional_data_for_seat_occupied_event(event)

    if event.event_type == 'ticket-revoked':
        yield from _get_additional_data_for_ticket_revoked_event(event)


def _get_additional_data_for_user_initiated_event(event: TicketEvent,
        users_by_id: Dict[UserID, UserTuple]) -> Iterator[Tuple[str, Any]]:
    initiator_id = event.data.get('initiator_id')
    if initiator_id is not None:
        yield 'initiator', users_by_id[initiator_id]


def _get_additional_data_for_seat_occupied_event(event: TicketEvent
                                                ) -> Iterator[Tuple[str, Any]]:
    seat_id = event.data['seat_id']
    seat = seat_service.find_seat(seat_id)
    yield 'seat_label', seat.label

    previous_seat_id = event.data.get('previous_seat_id')
    if previous_seat_id:
        previous_seat = seat_service.find_seat(previous_seat_id)
        yield 'previous_seat_label', previous_seat.label


def _get_additional_data_for_ticket_revoked_event(event: TicketEvent
                                                 ) -> Iterator[Tuple[str, Any]]:
    reason = event.data.get('reason')
    if reason:
        yield 'reason', reason
