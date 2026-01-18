"""
byceps.services.ticketing.log.ticket_log_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from sqlalchemy import select

from byceps.database import db
from byceps.services.ticketing.models.ticket import TicketID

from .dbmodels import DbTicketLogEntry
from .models import TicketLogEntry


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
