"""
byceps.services.seating.seat_reservation_domain_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from .models import SeatReservationPrecondition


def are_preconditions_met(
    preconditions: set[SeatReservationPrecondition],
    ticket_quantity: int,
    now: datetime,
) -> bool:
    """Return `True` if at least one of the preconditions is met."""
    return any(map(lambda p: p.is_met(ticket_quantity, now), preconditions))
