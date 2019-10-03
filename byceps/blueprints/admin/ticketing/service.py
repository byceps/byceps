"""
byceps.blueprints.admin.ticketing.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import Any, Dict, Iterator, Optional, Sequence, Set, Tuple

from ....services.seating import seat_service
from ....services.ticketing import event_service
from ....services.ticketing.models.ticket_event import (
    TicketEvent,
    TicketEventData,
)
from ....services.ticketing import ticket_service
from ....services.ticketing.transfer.models import TicketID
from ....services.user import service as user_service
from ....services.user.transfer.models import User


def get_events(ticket_id: TicketID) -> Iterator[TicketEventData]:
    events = event_service.get_events_for_ticket(ticket_id)
    events.insert(0, _fake_ticket_creation_event(ticket_id))

    user_ids = set(_find_values_for_keys(events, {
        'initiator_id',
        'appointed_seat_manager_id',
        'appointed_user_manager_id',
        'appointed_user_id',
        'checked_in_user_id',
        }))
    users = user_service.find_users(user_ids, include_avatars=True)
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

    data: TicketEventData = {}

    return TicketEvent(ticket.created_at, 'ticket-created', ticket.id, data)


def _find_values_for_keys(
    events: Sequence[TicketEvent], keys: Set[str]
) -> Iterator[Any]:
    for event in events:
        for key in keys:
            value = event.data.get(key)
            if value is not None:
                yield value


def _get_additional_data(
    event: TicketEvent, users_by_id: Dict[str, User]
) -> Iterator[Tuple[str, Any]]:
    if event.event_type in {
            'seat-manager-appointed',
            'seat-manager-withdrawn',
            'seat-occupied',
            'seat-released',
            'ticket-revoked',
            'user-appointed',
            'user-checked-in',
            'user-check-in-reverted',
            'user-manager-appointed',
            'user-manager-withdrawn',
            'user-withdrawn',
    }:
        yield from _get_additional_data_for_user_initiated_event(event,
                                                                 users_by_id)

    if event.event_type == 'seat-manager-appointed':
        yield _look_up_user_for_id(event, users_by_id,
            'appointed_seat_manager_id', 'appointed_seat_manager')

    if event.event_type == 'seat-occupied':
        yield from _get_additional_data_for_seat_occupied_event(event)

    if event.event_type == 'seat-released':
        yield from _get_additional_data_for_seat_released_event(event)

    if event.event_type == 'ticket-revoked':
        yield from _get_additional_data_for_ticket_revoked_event(event)

    if event.event_type == 'user-appointed':
        yield _look_up_user_for_id(event, users_by_id,
            'appointed_user_id', 'appointed_user')

    if event.event_type in {'user-checked-in', 'user-check-in-reverted'}:
        yield _look_up_user_for_id(event, users_by_id,
            'checked_in_user_id', 'checked_in_user')

    if event.event_type == 'user-manager-appointed':
        yield _look_up_user_for_id(event, users_by_id,
            'appointed_user_manager_id', 'appointed_user_manager')


def _get_additional_data_for_user_initiated_event(
    event: TicketEvent, users_by_id: Dict[str, User]
) -> Iterator[Tuple[str, Any]]:
    initiator_id = event.data.get('initiator_id')
    if initiator_id is not None:
        yield 'initiator', users_by_id[initiator_id]


def _get_additional_data_for_seat_occupied_event(
    event: TicketEvent
) -> Iterator[Tuple[str, Any]]:
    seat_id = event.data['seat_id']
    seat = seat_service.find_seat(seat_id)
    yield 'seat_label', seat.label

    previous_seat_id = event.data.get('previous_seat_id')
    if previous_seat_id:
        previous_seat = seat_service.find_seat(previous_seat_id)
        yield 'previous_seat_label', previous_seat.label


def _get_additional_data_for_seat_released_event(
    event: TicketEvent
) -> Iterator[Tuple[str, Any]]:
    seat_id = event.data.get('seat_id')
    if seat_id:
        seat = seat_service.find_seat(seat_id)
        yield 'seat_label', seat.label


def _get_additional_data_for_ticket_revoked_event(
    event: TicketEvent
) -> Iterator[Tuple[str, Any]]:
    reason = event.data.get('reason')
    if reason:
        yield 'reason', reason


def _look_up_user_for_id(
    event: TicketEvent,
    users_by_id: Dict[str, User],
    user_id_key: str,
    user_key: str,
) -> Tuple[str, Optional[User]]:
    user_id = event.data[user_id_key]
    user = users_by_id.get(user_id)
    return user_key, user
