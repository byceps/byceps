"""
byceps.services.seating.seat_reservation_repository
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from uuid import UUID

from sqlalchemy import delete, select

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


def delete_precondition(precondition_id: UUID) -> None:
    """Delete a reservation precondition."""
    db.session.execute(
        delete(DbSeatReservationPrecondition).filter_by(id=precondition_id)
    )

    db.session.commit()


def find_precondition(
    precondition_id: UUID,
) -> DbSeatReservationPrecondition | None:
    """Return a reservation precondition."""
    return db.session.get(DbSeatReservationPrecondition, precondition_id)


def get_preconditions(
    party_id: PartyID,
) -> set[DbSeatReservationPrecondition]:
    """Return all reservation preconditions for that party."""
    return set(
        db.session.scalars(
            select(DbSeatReservationPrecondition).filter_by(party_id=party_id)
        ).all()
    )
