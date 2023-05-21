"""
byceps.services.ticketing.dbmodels.checkin
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from byceps.database import db, generate_uuid7
from byceps.services.ticketing.models.ticket import TicketID
from byceps.typing import UserID


class DbTicketCheckIn(db.Model):
    """The check-in of a ticket."""

    __tablename__ = 'ticket_checkins'

    id = db.Column(db.Uuid, default=generate_uuid7, primary_key=True)
    occurred_at = db.Column(db.DateTime, nullable=False)
    ticket_id = db.Column(
        db.Uuid, db.ForeignKey('tickets.id'), index=True, nullable=False
    )
    initiator_id = db.Column(db.Uuid, db.ForeignKey('users.id'), nullable=False)

    def __init__(
        self,
        occurred_at: datetime,
        ticket_id: TicketID,
        initiator_id: UserID,
    ) -> None:
        self.occurred_at = occurred_at
        self.ticket_id = ticket_id
        self.initiator_id = initiator_id
