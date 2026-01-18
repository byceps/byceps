"""
byceps.services.seating.seat_reservation_domain_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from byceps.services.party.models import PartyID
from byceps.util.uuid import generate_uuid7

from .models import SeatReservationPrecondition


def create_precondition(
    party_id: PartyID,
    at_earliest: datetime,
    minimum_ticket_quantity: int,
) -> SeatReservationPrecondition:
    """Create a seat reservation precondition for the party."""
    return SeatReservationPrecondition(
        id=generate_uuid7(),
        party_id=party_id,
        at_earliest=at_earliest,
        minimum_ticket_quantity=minimum_ticket_quantity,
    )


def are_preconditions_met(
    preconditions: set[SeatReservationPrecondition],
    now: datetime,
    ticket_quantity: int,
) -> bool:
    """Return `True` if at least one of the preconditions is met."""
    return any(map(lambda p: p.is_met(now, ticket_quantity), preconditions))
