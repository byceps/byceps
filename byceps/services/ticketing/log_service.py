"""
byceps.services.ticketing.log_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from datetime import datetime

from sqlalchemy import select

from ...database import db

from .dbmodels.log import TicketLogEntry as DbTicketLogEntry
from .transfer.log import TicketLogEntry, TicketLogEntryData
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


def get_entries_for_ticket(ticket_id: TicketID) -> list[TicketLogEntry]:
    """Return the log entries for that ticket."""
    db_entries = db.session.execute(
        select(DbTicketLogEntry)
        .filter_by(ticket_id=ticket_id)
        .order_by(DbTicketLogEntry.occurred_at)
    ).scalars().all()

    return [_db_entity_to_entry(db_entry) for db_entry in db_entries]


def _db_entity_to_entry(db_entry: DbTicketLogEntry) -> TicketLogEntry:
    return TicketLogEntry(
        id=db_entry.id,
        occurred_at=db_entry.occurred_at,
        event_type=db_entry.event_type,
        ticket_id=db_entry.ticket_id,
        data=db_entry.data.copy(),
    )
