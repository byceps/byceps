"""
byceps.services.seating.seat_reservation_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from byceps.services.party.models import PartyID

from . import seat_reservation_domain_service, seat_reservation_repository
from .dbmodels.reservation import DbSeatReservationPrecondition
from .models import SeatReservationPrecondition


def create_precondition(
    party_id: PartyID,
    at_earliest: datetime,
    minimum_ticket_quantity: int,
) -> SeatReservationPrecondition:
    """Create a seat reservation precondition for the party."""
    precondition = seat_reservation_domain_service.create_precondition(
        party_id, at_earliest, minimum_ticket_quantity
    )

    seat_reservation_repository.create_precondition(precondition)

    return precondition


def get_preconditions(
    party_id: PartyID,
) -> set[DbSeatReservationPrecondition]:
    """Return all reservation preconditions for that party."""
    db_preconditions = seat_reservation_repository.get_preconditions(party_id)

    return {
        _db_entity_to_precondition(db_precondition)
        for db_precondition in db_preconditions
    }


def _db_entity_to_precondition(
    db_precondition: DbSeatReservationPrecondition,
) -> SeatReservationPrecondition:
    return SeatReservationPrecondition(
        id=db_precondition.id,
        party_id=db_precondition.party_id,
        at_earliest=db_precondition.at_earliest,
        minimum_ticket_quantity=db_precondition.minimum_ticket_quantity,
    )


def is_reservation_allowed(
    party_id: PartyID, ticket_quantity: int, now: datetime
) -> bool:
    """Return `True` if at least one of the preconditions is met."""
    preconditions = seat_reservation_repository.get_preconditions(party_id)

    if not preconditions:
        # Allow reservation if no preconditions are defined.
        return True

    return seat_reservation_domain_service.are_preconditions_met(
        preconditions, now, ticket_quantity
    )
