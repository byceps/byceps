"""
byceps.services.ticketing.log_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from datetime import datetime

from ...database import db

from .dbmodels.log import TicketLogEntry as DbTicketLogEntry, TicketLogEntryData
from .transfer.models import TicketID


def create_entry(
    event_type: str, ticket_id: TicketID, data: TicketLogEntryData
) -> None:
    """Create a ticket log entry."""
    entry = build_log_entry(event_type, ticket_id, data)

    db.session.add(entry)
    db.session.commit()


def build_log_entry(
    event_type: str, ticket_id: TicketID, data: TicketLogEntryData
) -> DbTicketLogEntry:
    """Assemble, but not persist, a ticket log entry."""
    now = datetime.utcnow()

    return DbTicketLogEntry(now, event_type, ticket_id, data)


def get_entries_for_ticket(ticket_id: TicketID) -> list[DbTicketLogEntry]:
    """Return the log entries for that ticket."""
    return db.session \
        .query(DbTicketLogEntry) \
        .filter_by(ticket_id=ticket_id) \
        .order_by(DbTicketLogEntry.occurred_at) \
        .all()
