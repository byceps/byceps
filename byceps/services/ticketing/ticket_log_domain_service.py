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
