"""
byceps.services.ticketing.models.ticket_event
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime
from typing import Any, Dict

from ....database import db, generate_uuid
from ....util.instances import ReprBuilder

from ..transfer.models import TicketID


TicketEventData = Dict[str, Any]


class TicketEvent(db.Model):
    """An event that refers to a ticket."""

    __tablename__ = 'ticket_events'

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    occurred_at = db.Column(db.DateTime, nullable=False)
    event_type = db.Column(db.UnicodeText, index=True, nullable=False)
    ticket_id = db.Column(db.Uuid, db.ForeignKey('tickets.id'), index=True, nullable=False)
    data = db.Column(db.JSONB)

    def __init__(
        self,
        occurred_at: datetime,
        event_type: str,
        ticket_id: TicketID,
        data: TicketEventData,
    ) -> None:
        self.occurred_at = occurred_at
        self.event_type = event_type
        self.ticket_id = ticket_id
        self.data = data

    def __repr__(self) -> str:
        return ReprBuilder(self) \
            .add_custom(repr(self.event_type)) \
            .add_with_lookup('ticket_id') \
            .add_with_lookup('data') \
            .build()
