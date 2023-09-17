"""
byceps.services.ticketing.dbmodels.checkin
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Mapped, mapped_column

from byceps.database import db
from byceps.services.ticketing.models.ticket import TicketID
from byceps.typing import UserID
from byceps.util.uuid import generate_uuid7


class DbTicketCheckIn(db.Model):
    """The check-in of a ticket."""

    __tablename__ = 'ticket_checkins'

    id: Mapped[UUID] = mapped_column(
        db.Uuid, default=generate_uuid7, primary_key=True
    )
    occurred_at: Mapped[datetime]
    ticket_id: Mapped[TicketID] = mapped_column(
        db.Uuid, db.ForeignKey('tickets.id'), index=True
    )
    initiator_id: Mapped[UserID] = mapped_column(
        db.Uuid, db.ForeignKey('users.id')
    )

    def __init__(
        self,
        occurred_at: datetime,
        ticket_id: TicketID,
        initiator_id: UserID,
    ) -> None:
        self.occurred_at = occurred_at
        self.ticket_id = ticket_id
        self.initiator_id = initiator_id
