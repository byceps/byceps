"""
byceps.services.seating.seat_reservation_repository
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from sqlalchemy import select

from byceps.database import db
from byceps.services.party.models import PartyID

from .dbmodels.reservation import DbSeatReservationPrecondition
from .models import SeatReservationPrecondition


def create_precondition(
    precondition: SeatReservationPrecondition,
) -> None:
    """Create a reservation precondition."""
    db_precondition = DbSeatReservationPrecondition(
        precondition.id,
        precondition.party_id,
        precondition.at_earliest,
        precondition.minimum_ticket_quantity,
    )
    db.session.add(db_precondition)
    db.session.commit()


def get_preconditions(
    party_id: PartyID,
) -> set[DbSeatReservationPrecondition]:
    """Return all reservation preconditions for that party."""
    return set(
        db.session.scalars(
            select(DbSeatReservationPrecondition).filter_by(party_id=party_id)
        ).all()
    )
