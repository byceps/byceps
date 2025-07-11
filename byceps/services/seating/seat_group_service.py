"""
byceps.services.seating.seat_group_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections.abc import Sequence

from byceps.services.party.models import PartyID
from byceps.services.ticketing import ticket_bundle_service
from byceps.services.ticketing.models.ticket import (
    TicketBundle,
    TicketBundleID,
    TicketCategoryID,
)
from byceps.util.result import Err, Ok, Result

from . import seat_group_domain_service, seat_group_repository, seat_service
from .dbmodels.seat_group import DbSeatGroup, DbSeatGroupOccupancy
from .errors import SeatingError
from .models import Seat, SeatGroup, SeatGroupID, SeatGroupOccupancy, SeatID


def create_group(
    party_id: PartyID,
    ticket_category_id: TicketCategoryID,
    title: str,
    seats: list[Seat],
) -> Result[SeatGroup, SeatingError]:
    """Create a seat group and assign the given seats."""
    creation_result = seat_group_domain_service.create_group(
        party_id, ticket_category_id, title, seats
    )
    match creation_result:
        case Ok(g):
            group = g
        case Err(e):
            return Err(e)

    seat_group_repository.create_group(group)

    return Ok(group)


def occupy_group(
    group: SeatGroup, ticket_bundle: TicketBundle
) -> Result[SeatGroupOccupancy, SeatingError]:
    """Occupy the seat group with that ticket bundle."""
    group_availability_result = _ensure_group_is_available(group)
    if group_availability_result.is_err():
        return Err(group_availability_result.unwrap_err())

    occupation_result = seat_group_domain_service.occupy_group(
        group, ticket_bundle
    )
    match occupation_result:
        case Ok(sgo):
            occupancy = sgo
        case Err(e):
            return Err(e)

    db_tickets = ticket_bundle_service.get_tickets_for_bundle(ticket_bundle.id)

    db_occupation_result = seat_group_repository.occupy_group(
        group, occupancy, db_tickets
    )
    match db_occupation_result:
        case Err(e):
            return Err(e)

    return Ok(occupancy)


def switch_group(
    occupancy: SeatGroupOccupancy, target_group: SeatGroup
) -> Result[None, SeatingError]:
    """Switch ticket bundle to another seat group."""
    db_ticket_bundle = ticket_bundle_service.get_bundle(
        occupancy.ticket_bundle_id
    )
    ticket_bundle = ticket_bundle_service.db_entity_to_ticket_bundle(
        db_ticket_bundle
    )

    group_availability_result = _ensure_group_is_available(target_group)
    if group_availability_result.is_err():
        return Err(group_availability_result.unwrap_err())

    switch_result = seat_group_domain_service.switch_group(
        target_group, ticket_bundle
    )
    match switch_result:
        case Err(e):
            return Err(e)

    db_tickets = ticket_bundle_service.get_tickets_for_bundle(
        occupancy.ticket_bundle_id
    )

    db_switch_result = seat_group_repository.switch_group(
        occupancy, target_group, db_tickets
    )
    match db_switch_result:
        case Err(e):
            return Err(e)

    return Ok(None)


def _ensure_group_is_available(group: SeatGroup) -> Result[None, SeatingError]:
    """Return an error if the seat group is occupied."""
    occupancy = find_occupancy_for_group(group.id)
    if occupancy is not None:
        return Err(SeatingError('Seat group is already occupied.'))

    return Ok(None)


def release_group(
    group_id: SeatGroupID,
) -> Result[None, SeatingError]:
    """Release a seat group so it becomes available again."""
    return seat_group_repository.release_group(group_id)


def count_groups_for_party(party_id: PartyID) -> int:
    """Return the number of seat groups for that party."""
    return seat_group_repository.count_groups_for_party(party_id)


def find_group(group_id: SeatGroupID) -> SeatGroup | None:
    """Return the seat group with that id, or `None` if not found."""
    db_group_and_seat_ids = seat_group_repository.find_group(group_id)

    if db_group_and_seat_ids is None:
        return None

    db_group, seat_ids = db_group_and_seat_ids
    seats = seat_service.get_seats(seat_ids)

    return _db_entity_to_group(db_group, seats)


def find_group_occupied_by_ticket_bundle(
    ticket_bundle_id: TicketBundleID,
) -> SeatGroupID | None:
    """Return the ID of the seat group occupied by that ticket bundle,
    or `None` if not found.
    """
    return seat_group_repository.find_group_occupied_by_ticket_bundle(
        ticket_bundle_id
    )


def find_occupancy_for_group(
    group_id: SeatGroupID,
) -> SeatGroupOccupancy | None:
    """Return the occupancy for that seat group, or `None` if not found."""
    db_occupancy = seat_group_repository.find_occupancy_for_group(group_id)

    if db_occupancy is None:
        return None

    return _db_entity_to_occupancy(db_occupancy)


def get_all_groups_for_party(party_id: PartyID) -> Sequence[DbSeatGroup]:
    """Return all seat groups for that party."""
    return seat_group_repository.get_all_groups_for_party(party_id)


def is_seat_part_of_a_group(seat_id: SeatID) -> bool:
    """Return whether or not the seat is part of a seat group."""
    return seat_group_repository.is_seat_part_of_a_group(seat_id)


def _db_entity_to_group(db_group: DbSeatGroup, seats: list[Seat]) -> SeatGroup:
    if db_group.seat_quantity != len(seats):
        raise ValueError(
            'Expected seat quantity in group does not match number of seats'
        )

    return SeatGroup(
        id=db_group.id,
        party_id=db_group.party_id,
        ticket_category_id=db_group.ticket_category_id,
        seat_quantity=db_group.seat_quantity,
        title=db_group.title,
        seats=seats,
    )


def _db_entity_to_occupancy(
    db_occupancy: DbSeatGroupOccupancy,
) -> SeatGroupOccupancy:
    return SeatGroupOccupancy(
        id=db_occupancy.id,
        group_id=db_occupancy.group_id,
        ticket_bundle_id=db_occupancy.ticket_bundle_id,
    )
