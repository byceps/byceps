"""
byceps.services.seating.dbmodels.reservation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Mapped, mapped_column

from byceps.database import db
from byceps.services.party.models import PartyID


class DbSeatReservationPrecondition(db.Model):
    """A seat reservation precondition."""

    __tablename__ = 'seat_reservation_preconditions'

    id: Mapped[UUID] = mapped_column(db.Uuid, primary_key=True)
    party_id: Mapped[PartyID] = mapped_column(
        db.UnicodeText, db.ForeignKey('parties.id'), index=True
    )
    at_earliest: Mapped[datetime]
    minimum_ticket_quantity: Mapped[int]

    def __init__(
        self,
        precondition_id: UUID,
        party_id: PartyID,
        at_earliest: datetime,
        minimum_ticket_quantity: int,
    ) -> None:
        self.id = precondition_id
        self.party_id = party_id
        self.at_earliest = at_earliest
        self.minimum_ticket_quantity = minimum_ticket_quantity
