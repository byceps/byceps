"""
byceps.services.ticketing.log.ticket_log_domain_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from byceps.services.seating.models import SeatID
from byceps.services.ticketing.models.ticket import TicketID
from byceps.services.user.models.user import User, UserID
from byceps.util.uuid import generate_uuid7

from .models import TicketLogEntry, TicketLogEntryData


def _build_entry(
    event_type: str,
    ticket_id: TicketID,
    data: TicketLogEntryData,
    *,
    occurred_at: datetime | None = None,
) -> TicketLogEntry:
    """Assemble a ticket log entry."""
    entry_id = generate_uuid7()

    if occurred_at is None:
        occurred_at = datetime.utcnow()

    return TicketLogEntry(
        id=entry_id,
        occurred_at=occurred_at,
        event_type=event_type,
        ticket_id=ticket_id,
        data=data,
    )


def build_ticket_code_changed_entry(
    ticket_id: TicketID, old_code: str, new_code: str, initiator: User
) -> TicketLogEntry:
    """Assemble a 'ticket code changed' log entry."""
    return _build_entry(
        'ticket-code-changed',
        ticket_id,
        {
            'old_code': old_code,
            'new_code': new_code,
            'initiator_id': str(initiator.id),
        },
    )


def build_ticket_revoked_entry(
    ticket_id: TicketID, initiator: User, reason: str | None = None
) -> TicketLogEntry:
    """Assemble a 'ticket revoked' log entry."""
    data = {
        'initiator_id': str(initiator.id),
    }

    if reason:
        data['reason'] = reason

    return _build_entry('ticket-revoked', ticket_id, data)


def build_user_manager_appointed_entry(
    ticket_id: TicketID, manager: User, initiator: User
) -> TicketLogEntry:
    """Assemble a 'user manager appointed' log entry."""
    return _build_entry(
        'user-manager-appointed',
        ticket_id,
        {
            'appointed_user_manager_id': str(manager.id),
            'initiator_id': str(initiator.id),
        },
    )


def build_user_manager_withdrawn_entry(
    ticket_id: TicketID, initiator: User
) -> TicketLogEntry:
    """Assemble a 'user manager withdrawn' log entry."""
    return _build_entry(
        'user-manager-withdrawn',
        ticket_id,
        {
            'initiator_id': str(initiator.id),
        },
    )


def build_user_appointed_entry(
    ticket_id: TicketID, user: User, initiator: User
) -> TicketLogEntry:
    """Assemble a 'user appointed' log entry."""
    return _build_entry(
        'user-appointed',
        ticket_id,
        {
            'appointed_user_id': str(user.id),
            'initiator_id': str(initiator.id),
        },
    )


def build_user_withdrawn_entry(
    ticket_id: TicketID, initiator: User
) -> TicketLogEntry:
    """Assemble a 'user withdrawn' log entry."""
    return _build_entry(
        'user-withdrawn',
        ticket_id,
        {
            'initiator_id': str(initiator.id),
        },
    )


def build_seat_manager_appointed_entry(
    ticket_id: TicketID, manager: User, initiator: User
) -> TicketLogEntry:
    """Assemble a 'seat manager appointed' log entry."""
    return _build_entry(
        'seat-manager-appointed',
        ticket_id,
        {
            'appointed_seat_manager_id': str(manager.id),
            'initiator_id': str(initiator.id),
        },
    )


def build_seat_manager_withdrawn_entry(
    ticket_id: TicketID, initiator: User
) -> TicketLogEntry:
    """Assemble a 'seat manager withdrawn' log entry."""
    return _build_entry(
        'seat-manager-withdrawn',
        ticket_id,
        {
            'initiator_id': str(initiator.id),
        },
    )


def build_occupy_seat_entry(
    ticket_id: TicketID,
    seat_id: SeatID,
    previous_seat_id: SeatID | None,
    initiator: User,
) -> TicketLogEntry:
    """Assemble an 'occupy seat' log entry."""
    data = {
        'seat_id': str(seat_id),
        'initiator_id': str(initiator.id),
    }

    if previous_seat_id is not None:
        data['previous_seat_id'] = str(previous_seat_id)

    return _build_entry('seat-occupied', ticket_id, data)


def build_release_seat_entry(
    ticket_id: TicketID,
    seat_id: SeatID,
    initiator: User,
) -> TicketLogEntry:
    """Assemble a 'release seat' log entry."""
    return _build_entry(
        'seat-released',
        ticket_id,
        {
            'seat_id': str(seat_id),
            'initiator_id': str(initiator.id),
        },
    )


def build_user_checked_in_entry(
    ticket_id: TicketID,
    user: User,
    initiator: User,
    *,
    occurred_at: datetime | None = None,
) -> TicketLogEntry:
    """Assemble a 'user checked in' log entry."""
    return _build_entry(
        'user-checked-in',
        ticket_id,
        {
            'checked_in_user_id': str(user.id),
            'initiator_id': str(initiator.id),
        },
        occurred_at=occurred_at,
    )


def build_user_check_in_reverted_entry(
    ticket_id: TicketID,
    user_id: UserID,
    initiator: User,
) -> TicketLogEntry:
    """Assemble a 'user check-in reverted' log entry."""
    return _build_entry(
        'user-check-in-reverted',
        ticket_id,
        {
            'checked_in_user_id': str(user_id),
            'initiator_id': str(initiator.id),
        },
    )
