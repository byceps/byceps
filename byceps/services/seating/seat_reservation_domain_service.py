"""
byceps.services.seating.seat_reservation_domain_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from byceps.services.party.models import PartyID
from byceps.util.uuid import generate_uuid7

from .models import SeatReservationPrecondition


def create_precondition(
    party_id: PartyID,
    minimum_ticket_quantity: int,
    at_earliest: datetime,
) -> SeatReservationPrecondition:
    """Create a seat reservation precondition for the party."""
    return SeatReservationPrecondition(
        id=generate_uuid7(),
        party_id=party_id,
        minimum_ticket_quantity=minimum_ticket_quantity,
        at_earliest=at_earliest,
    )


def are_preconditions_met(
    preconditions: set[SeatReservationPrecondition],
    ticket_quantity: int,
    now: datetime,
) -> bool:
    """Return `True` if at least one of the preconditions is met."""
    return any(map(lambda p: p.is_met(ticket_quantity, now), preconditions))
