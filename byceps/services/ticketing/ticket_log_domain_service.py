"""
byceps.services.ticketing.ticket_log_domain_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

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
