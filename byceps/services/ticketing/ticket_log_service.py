"""
byceps.services.ticketing.ticket_log_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import select

from byceps.database import db, generate_uuid7

from .dbmodels.log import DbTicketLogEntry
from .models.log import TicketLogEntry, TicketLogEntryData
from .models.ticket import TicketID


def build_db_entry(
    event_type: str,
    ticket_id: TicketID,
    data: TicketLogEntryData,
    *,
    occurred_at: datetime | None = None,
) -> DbTicketLogEntry:
    """Assemble, but not persist, a ticket log entry."""
    entry_id = generate_uuid7()

    if occurred_at is None:
        occurred_at = datetime.utcnow()

    return DbTicketLogEntry(entry_id, occurred_at, event_type, ticket_id, data)


def to_db_entry(entry: TicketLogEntry) -> DbTicketLogEntry:
    """Convert log entry to database entity."""
    return DbTicketLogEntry(
        entry.id,
        entry.occurred_at,
        entry.event_type,
        entry.ticket_id,
        entry.data,
    )


def get_entries_for_ticket(ticket_id: TicketID) -> list[TicketLogEntry]:
    """Return the log entries for that ticket."""
    db_entries = db.session.scalars(
        select(DbTicketLogEntry)
        .filter_by(ticket_id=ticket_id)
        .order_by(DbTicketLogEntry.occurred_at)
    ).all()

    return [_db_entity_to_entry(db_entry) for db_entry in db_entries]


def _db_entity_to_entry(db_entry: DbTicketLogEntry) -> TicketLogEntry:
    return TicketLogEntry(
        id=db_entry.id,
        occurred_at=db_entry.occurred_at,
        event_type=db_entry.event_type,
        ticket_id=db_entry.ticket_id,
        data=db_entry.data.copy(),
    )
