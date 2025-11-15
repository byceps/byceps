"""
byceps.services.ticketing.ticket_log_domain_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from byceps.services.user.models.user import User
from byceps.util.uuid import generate_uuid7

from .models.log import TicketLogEntry, TicketLogEntryData
from .models.ticket import TicketID


def build_entry(
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
    return build_entry(
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

    return build_entry('ticket-revoked', ticket_id, data)


def build_user_manager_appointed_entry(
    ticket_id: TicketID, manager: User, initiator: User
) -> TicketLogEntry:
    """Assemble a 'user manager appointed' log entry."""
    return build_entry(
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
    return build_entry(
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
    return build_entry(
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
    return build_entry(
        'user-withdrawn',
        ticket_id,
        {
            'initiator_id': str(initiator.id),
        },
    )
