"""
byceps.services.seating.seat_group_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.services.party import party_service
from byceps.services.party.models import PartyID
from byceps.services.ticketing import ticket_bundle_service
from byceps.services.ticketing.models.ticket import (
    TicketBundle,
    TicketBundleID,
    TicketCategoryID,
)
from byceps.services.user.models.user import User
from byceps.util.result import Err, Ok, Result

from . import seat_group_domain_service, seat_group_repository, seat_service
from .dbmodels.seat_group import DbSeatGroup, DbSeatGroupOccupancy
from .errors import SeatingError
from .events import SeatGroupOccupiedEvent, SeatGroupReleasedEvent
from .models import Seat, SeatGroup, SeatGroupID, SeatGroupOccupancy, SeatID


def create_group(
    party_id: PartyID,
    ticket_category_id: TicketCategoryID,
    title: str,
    seats: list[Seat],
) -> Result[SeatGroup, SeatingError]:
    """Create a seat group and assign the given seats."""
    match seat_group_domain_service.create_group(
        party_id, ticket_category_id, title, seats
    ):
        case Ok(group):
            pass
        case Err(e):
            return Err(e)

    seat_group_repository.create_group(group)

    return Ok(group)


def occupy_group(
    group: SeatGroup, ticket_bundle: TicketBundle, initiator: User
) -> Result[tuple[SeatGroupOccupancy, SeatGroupOccupiedEvent], SeatingError]:
    """Occupy the seat group with that ticket bundle."""
    match _ensure_group_is_available(group):
        case Err(e):
            return Err(e)

    party = party_service.get_party(group.party_id)

    match seat_group_domain_service.occupy_group(
        party, group, ticket_bundle, initiator
    ):
        case Ok((occupancy, event)):
            pass
        case Err(e):
            return Err(e)

    db_tickets = ticket_bundle_service.get_tickets_for_bundle(ticket_bundle.id)

    match seat_group_repository.occupy_group(group, occupancy, db_tickets):
        case Err(e):
            return Err(e)

    return Ok((occupancy, event))


def switch_group(
    occupancy: SeatGroupOccupancy, new_group: SeatGroup, initiator: User
) -> Result[
    tuple[SeatGroupReleasedEvent, SeatGroupOccupiedEvent], SeatingError
]:
    """Switch ticket bundle to another seat group."""
    db_ticket_bundle = ticket_bundle_service.get_bundle(
        occupancy.ticket_bundle_id
    )
    ticket_bundle = ticket_bundle_service.db_entity_to_ticket_bundle(
        db_ticket_bundle
    )

    old_group_id = ticket_bundle.occupied_seat_group_id
    if not old_group_id:
        return Err(SeatingError('Ticket bundle occupies no seat group.'))

    old_group = find_group(old_group_id)
    if not old_group:
        return Err(SeatingError('Seat group to switch away from not found.'))

    match _ensure_group_is_available(new_group):
        case Err(e):
            return Err(e)

    party = party_service.get_party(new_group.party_id)

    match seat_group_domain_service.switch_group(
        party, old_group, new_group, ticket_bundle, initiator
    ):
        case Ok((release_event, occupation_event)):
            pass
        case Err(e):
            return Err(e)

    db_tickets = ticket_bundle_service.get_tickets_for_bundle(
        occupancy.ticket_bundle_id
    )

    match seat_group_repository.switch_group(occupancy, new_group, db_tickets):
        case Err(e):
            return Err(e)

    return Ok((release_event, occupation_event))


def _ensure_group_is_available(group: SeatGroup) -> Result[None, SeatingError]:
    """Return an error if the seat group is occupied."""
    occupancy = find_occupancy_for_group(group.id)
    if occupancy is not None:
        return Err(SeatingError('Seat group is already occupied.'))

    return Ok(None)


def release_group(
    group_id: SeatGroupID, initiator: User
) -> Result[SeatGroupReleasedEvent, SeatingError]:
    """Release a seat group so it becomes available again."""
    group = find_group(group_id)
    if not group:
        return Err(SeatingError('Seat group to release not found.'))

    occupancy = find_occupancy_for_group(group.id)
    if not occupancy:
        return Err(SeatingError('Seat group to release is not occupied.'))

    party = party_service.get_party(group.party_id)

    match seat_group_domain_service.release_group(party, group, initiator):
        case Ok(event):
            pass
        case Err(e):
            return Err(e)

    match seat_group_repository.release_group(group_id):
        case Err(e):
            return Err(e)

    return Ok(event)


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


def get_groups_for_party(party_id: PartyID) -> list[SeatGroup]:
    """Return all seat groups for that party."""

    def _db_seat_group_to_seat_group(db_group: DbSeatGroup) -> SeatGroup:
        seat_ids = {db_seat.id for db_seat in db_group.seats}
        seats = seat_service.get_seats(seat_ids)

        return _db_entity_to_group(db_group, seats)

    db_groups = get_db_groups_for_party(party_id)
    return [_db_seat_group_to_seat_group(db_group) for db_group in db_groups]


def get_db_groups_for_party(party_id: PartyID) -> list[DbSeatGroup]:
    """Return all seat groups for that party."""
    return list(seat_group_repository.get_groups_for_party(party_id))


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
        group_id=db_occupancy.seat_group_id,
        ticket_bundle_id=db_occupancy.ticket_bundle_id,
    )
