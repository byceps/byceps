"""
byceps.services.seating.seat_group_domain_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.services.party.models import PartyID
from byceps.services.ticketing.models.ticket import (
    TicketBundle,
    TicketCategoryID,
)
from byceps.util.result import Err, Ok, Result
from byceps.util.uuid import generate_uuid7

from .errors import SeatingError
from .models import Seat, SeatGroup, SeatGroupID, SeatGroupOccupancy


def create_group(
    party_id: PartyID,
    ticket_category_id: TicketCategoryID,
    title: str,
    seats: list[Seat],
) -> Result[SeatGroup, SeatingError]:
    """Create a seat group and assign the given seats."""
    seat_quantity = len(seats)
    if seat_quantity == 0:
        return Err(SeatingError('No seats specified.'))

    ticket_category_ids = {seat.category_id for seat in seats}
    if len(ticket_category_ids) != 1 or (
        ticket_category_id not in ticket_category_ids
    ):
        return Err(
            SeatingError("Seats' ticket category IDs do not match the group's.")
        )

    group_id = SeatGroupID(generate_uuid7())

    group = SeatGroup(
        id=group_id,
        party_id=party_id,
        ticket_category_id=ticket_category_id,
        seat_quantity=seat_quantity,
        title=title,
        seats=list(seats),
    )

    return Ok(group)


def occupy_group(
    group: SeatGroup, ticket_bundle: TicketBundle
) -> Result[SeatGroupOccupancy, SeatingError]:
    """Occupy the seat group with that ticket bundle."""
    match _ensure_ticket_bundle_is_available(ticket_bundle):
        case Err(e):
            return Err(e)

    match _ensure_categories_match(group, ticket_bundle):
        case Err(e):
            return Err(e)

    match _ensure_quantities_match(group, ticket_bundle):
        case Err(e):
            return Err(e)

    match _ensure_seats_are_unoccupied(group):
        case Err(e):
            return Err(e)

    occupancy = SeatGroupOccupancy(
        id=generate_uuid7(),
        group_id=group.id,
        ticket_bundle_id=ticket_bundle.id,
    )

    return Ok(occupancy)


def switch_group(
    target_group: SeatGroup, ticket_bundle: TicketBundle
) -> Result[None, SeatingError]:
    """Switch ticket bundle to another seat group."""
    match _ensure_ticket_bundle_is_available(ticket_bundle):
        case Err(e):
            return Err(e)

    match _ensure_categories_match(target_group, ticket_bundle):
        case Err(e):
            return Err(e)

    match _ensure_quantities_match(target_group, ticket_bundle):
        case Err(e):
            return Err(e)

    match _ensure_seats_are_unoccupied(target_group):
        case Err(e):
            return Err(e)

    return Ok(None)


def _ensure_ticket_bundle_is_available(
    bundle: TicketBundle,
) -> Result[None, SeatingError]:
    """Return an error if the ticket bundle already occupies a seat group."""
    if bundle.occupied_seat_group_id:
        return Err(SeatingError('Ticket bundle already occupies a seat group.'))

    return Ok(None)


def _ensure_categories_match(
    group: SeatGroup, ticket_bundle: TicketBundle
) -> Result[None, SeatingError]:
    """Return an error if the seat group's and the ticket bundle's
    categories don't match.
    """
    if group.ticket_category_id != ticket_bundle.ticket_category.id:
        return Err(SeatingError('Seat and ticket categories do not match.'))

    return Ok(None)


def _ensure_quantities_match(
    group: SeatGroup, ticket_bundle: TicketBundle
) -> Result[None, SeatingError]:
    """Return an error if

    - the defined and actual seat quantity of the seat group or
    - the defined and actual ticket quantity of the ticket bundle or
    - the defined quantities of the seat group and the ticket bundle or
    - the actual quantities of seats and tickets

    don't match.
    """
    if group.seat_quantity != len(group.seats):
        return Err(
            SeatingError(
                'Defined and actual seat quantities in seat group do not match.'
            )
        )

    if ticket_bundle.ticket_quantity != len(ticket_bundle.ticket_ids):
        return Err(
            SeatingError(
                'Defined and actual ticket quantities in tucket bundle do not match.'
            )
        )

    if group.seat_quantity != ticket_bundle.ticket_quantity:
        return Err(SeatingError('Seat and ticket quantities do not match.'))

    if len(group.seats) != len(ticket_bundle.ticket_ids):
        return Err(
            SeatingError(
                'The actual quantities of seats and tickets do not match.'
            )
        )

    return Ok(None)


def _ensure_seats_are_unoccupied(
    group: SeatGroup,
) -> Result[None, SeatingError]:
    """Return an error if any of the seats is occupied."""
    for seat in group.seats:
        occupying_ticket_id = seat.occupied_by_ticket_id
        if occupying_ticket_id:
            return Err(
                SeatingError(
                    f'Seat {seat.id} is already occupied by ticket {occupying_ticket_id}; seat cannot be occupied.'
                )
            )

    return Ok(None)
