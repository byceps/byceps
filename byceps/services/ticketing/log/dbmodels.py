"""
byceps.services.ticketing.log.dbmodels
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Mapped, mapped_column

from byceps.database import db
from byceps.services.ticketing.models.ticket import TicketID
from byceps.util.instances import ReprBuilder

from .models import TicketLogEntryData


class DbTicketLogEntry(db.Model):
    """A log entry regarding a ticket."""

    __tablename__ = 'ticket_log_entries'

    id: Mapped[UUID] = mapped_column(db.Uuid, primary_key=True)
    occurred_at: Mapped[datetime]
    event_type: Mapped[str] = mapped_column(db.UnicodeText, index=True)
    ticket_id: Mapped[TicketID] = mapped_column(
        db.Uuid, db.ForeignKey('tickets.id'), index=True
    )
    data: Mapped[TicketLogEntryData] = mapped_column(db.JSONB)

    def __init__(
        self,
        id: UUID,
        occurred_at: datetime,
        event_type: str,
        ticket_id: TicketID,
        data: TicketLogEntryData,
    ) -> None:
        self.id = id
        self.occurred_at = occurred_at
        self.event_type = event_type
        self.ticket_id = ticket_id
        self.data = data

    def __repr__(self) -> str:
        return (
            ReprBuilder(self)
            .add_custom(repr(self.event_type))
            .add_with_lookup('ticket_id')
            .add_with_lookup('data')
            .build()
        )
