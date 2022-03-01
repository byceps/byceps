"""
byceps.blueprints.admin.ticketing.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from typing import Any, Iterable, Iterator, Optional
from uuid import UUID

from ....services.seating import seat_service
from ....services.ticketing import log_service, ticket_service
from ....services.ticketing.transfer.log import (
    TicketLogEntry,
    TicketLogEntryData,
)
from ....services.ticketing.transfer.models import TicketID
from ....services.user import service as user_service
from ....services.user.transfer.models import User


def get_log_entries(ticket_id: TicketID) -> Iterator[TicketLogEntryData]:
    log_entries = log_service.get_entries_for_ticket(ticket_id)
    log_entries.insert(0, _fake_ticket_creation_log_entry(ticket_id))

    users_by_id = _get_users_by_id(log_entries)

    for log_entry in log_entries:
        data = {
            'event_type': log_entry.event_type,
            'occurred_at': log_entry.occurred_at,
            'data': log_entry.data,
        }

        data.update(_get_additional_data(log_entry, users_by_id))

        yield data


def _fake_ticket_creation_log_entry(ticket_id: TicketID) -> TicketLogEntry:
    ticket = ticket_service.get_ticket(ticket_id)
    data: TicketLogEntryData = {}

    return TicketLogEntry(
        id=UUID('00000000-0000-0000-0000-000000000001'),
        occurred_at=ticket.created_at,
        event_type='ticket-created',
        ticket_id=ticket.id,
        data=data,
    )


def _get_users_by_id(
    log_entries: Iterable[TicketLogEntry],
) -> dict[str, User]:
    user_ids = set(
        _find_values_for_keys(
            log_entries,
            {
                'initiator_id',
                'appointed_seat_manager_id',
                'appointed_user_manager_id',
                'appointed_user_id',
                'checked_in_user_id',
            },
        )
    )

    users = user_service.get_users(user_ids, include_avatars=True)
    return {str(user.id): user for user in users}


def _find_values_for_keys(
    log_entries: Iterable[TicketLogEntry], keys: set[str]
) -> Iterator[Any]:
    for log_entry in log_entries:
        for key in keys:
            value = log_entry.data.get(key)
            if value is not None:
                yield value


def _get_additional_data(
    log_entry: TicketLogEntry, users_by_id: dict[str, User]
) -> Iterator[tuple[str, Any]]:
    yield from _get_initiators(log_entry, users_by_id)

    if log_entry.event_type == 'seat-manager-appointed':
        yield _look_up_user_for_id(
            log_entry,
            users_by_id,
            'appointed_seat_manager_id',
            'appointed_seat_manager',
        )

    if log_entry.event_type == 'seat-occupied':
        yield from _get_additional_data_for_seat_occupied_event(log_entry)

    if log_entry.event_type == 'seat-released':
        yield from _get_additional_data_for_seat_released_event(log_entry)

    if log_entry.event_type == 'ticket-revoked':
        yield from _get_additional_data_for_ticket_revoked_event(log_entry)

    if log_entry.event_type == 'user-appointed':
        yield _look_up_user_for_id(
            log_entry, users_by_id, 'appointed_user_id', 'appointed_user'
        )

    if log_entry.event_type in {'user-checked-in', 'user-check-in-reverted'}:
        yield _look_up_user_for_id(
            log_entry, users_by_id, 'checked_in_user_id', 'checked_in_user'
        )

    if log_entry.event_type == 'user-manager-appointed':
        yield _look_up_user_for_id(
            log_entry,
            users_by_id,
            'appointed_user_manager_id',
            'appointed_user_manager',
        )


def _get_initiators(
    log_entry: TicketLogEntry, users_by_id: dict[str, User]
) -> Iterator[tuple[str, Any]]:
    if log_entry.event_type in {
        'seat-manager-appointed',
        'seat-manager-withdrawn',
        'seat-occupied',
        'seat-released',
        'ticket-code-changed',
        'ticket-revoked',
        'user-appointed',
        'user-checked-in',
        'user-check-in-reverted',
        'user-manager-appointed',
        'user-manager-withdrawn',
        'user-withdrawn',
    }:
        yield from _get_additional_data_for_user_initiated_event(
            log_entry, users_by_id
        )


def _get_additional_data_for_user_initiated_event(
    log_entry: TicketLogEntry, users_by_id: dict[str, User]
) -> Iterator[tuple[str, Any]]:
    initiator_id = log_entry.data.get('initiator_id')
    if initiator_id is not None:
        yield 'initiator', users_by_id[initiator_id]


def _get_additional_data_for_seat_occupied_event(
    log_entry: TicketLogEntry,
) -> Iterator[tuple[str, Any]]:
    seat_id = log_entry.data['seat_id']
    seat = seat_service.get_seat(seat_id)
    yield 'seat_label', seat.label

    previous_seat_id = log_entry.data.get('previous_seat_id')
    if previous_seat_id:
        previous_seat = seat_service.get_seat(previous_seat_id)
        yield 'previous_seat_label', previous_seat.label


def _get_additional_data_for_seat_released_event(
    log_entry: TicketLogEntry,
) -> Iterator[tuple[str, Any]]:
    seat_id = log_entry.data.get('seat_id')
    if seat_id:
        seat = seat_service.get_seat(seat_id)
        yield 'seat_label', seat.label


def _get_additional_data_for_ticket_revoked_event(
    log_entry: TicketLogEntry,
) -> Iterator[tuple[str, Any]]:
    reason = log_entry.data.get('reason')
    if reason:
        yield 'reason', reason


def _look_up_user_for_id(
    log_entry: TicketLogEntry,
    users_by_id: dict[str, User],
    user_id_key: str,
    user_key: str,
) -> tuple[str, Optional[User]]:
    user_id = log_entry.data[user_id_key]
    user = users_by_id.get(user_id)
    return user_key, user
