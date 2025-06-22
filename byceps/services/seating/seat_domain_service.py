"""
byceps.services.seating.seat_domain_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections.abc import Iterable

from byceps.services.ticketing.models.ticket import TicketCategoryID, TicketID
from byceps.util.uuid import generate_uuid7

from .models import Seat, SeatID, SeatingAreaID, SeatUtilization


def create_seat(
    area_id: SeatingAreaID,
    coord_x: int,
    coord_y: int,
    category_id: TicketCategoryID,
    *,
    rotation: int | None = None,
    label: str | None = None,
    type_: str | None = None,
    occupied_by_ticket_id: TicketID | None = None,
) -> Seat:
    """Create a seat."""
    seat_id = SeatID(generate_uuid7())

    return Seat(
        id=seat_id,
        area_id=area_id,
        coord_x=coord_x,
        coord_y=coord_y,
        rotation=rotation,
        category_id=category_id,
        label=label,
        type_=type_,
        occupied_by_ticket_id=occupied_by_ticket_id,
    )


def aggregate_seat_utilizations(
    seat_utilizations: Iterable[SeatUtilization],
) -> SeatUtilization:
    """Aggregate multiple seat utilizations into one."""
    return SeatUtilization(
        occupied=sum(su.occupied for su in seat_utilizations),
        total=sum(su.total for su in seat_utilizations),
    )
