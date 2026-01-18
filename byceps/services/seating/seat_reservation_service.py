"""
byceps.services.seating.seat_reservation_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime
from uuid import UUID

from byceps.services.party.models import PartyID
from byceps.services.ticketing import ticket_service
from byceps.services.ticketing.dbmodels.ticket import DbTicket
from byceps.services.ticketing.models.ticket import TicketCode
from byceps.services.user import user_service
from byceps.services.user.models.user import User, UserID

from . import seat_reservation_domain_service, seat_reservation_repository
from .dbmodels.reservation import DbSeatReservationPrecondition
from .models import ManagedTicket, SeatReservationPrecondition


# preconditions


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


def delete_precondition(precondition_id: UUID) -> None:
    """Delete a reservation precondition."""
    seat_reservation_repository.delete_precondition(precondition_id)


def find_precondition(
    precondition_id: UUID,
) -> SeatReservationPrecondition | None:
    """Return a reservation precondition."""
    db_precondition = seat_reservation_repository.find_precondition(
        precondition_id
    )

    if not db_precondition:
        return None

    return _db_entity_to_precondition(db_precondition)


def get_preconditions(party_id: PartyID) -> set[SeatReservationPrecondition]:
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
    party_id: PartyID, now: datetime, ticket_quantity: int
) -> bool:
    """Return `True` if at least one of the preconditions is met."""
    preconditions = get_preconditions(party_id)

    if not preconditions:
        # Allow reservation if no preconditions are defined.
        return True

    return seat_reservation_domain_service.are_preconditions_met(
        preconditions, now, ticket_quantity
    )


# managed tickets


def get_managed_tickets(
    seat_manager_id: UserID, party_id: PartyID
) -> list[ManagedTicket]:
    db_tickets = ticket_service.get_tickets_for_seat_manager(
        seat_manager_id, party_id
    )

    user_ids = {
        db_ticket.used_by_id for db_ticket in db_tickets if db_ticket.used_by_id
    }

    users_by_id = user_service.get_users_indexed_by_id(
        user_ids, include_avatars=False
    )

    return [
        _build_managed_ticket(db_ticket, users_by_id)
        for db_ticket in db_tickets
    ]


def _build_managed_ticket(
    db_ticket: DbTicket, users_by_id: dict[UserID, User]
) -> ManagedTicket:
    occupies_seat = db_ticket.occupied_seat is not None

    seat_label = (
        db_ticket.occupied_seat.label
        if (db_ticket.occupied_seat is not None)
        else None
    )

    user: User | None
    if db_ticket.used_by_id is not None:
        user = users_by_id[db_ticket.used_by_id]
    else:
        user = None

    return ManagedTicket(
        id=db_ticket.id,
        code=TicketCode(db_ticket.code),
        category_label=db_ticket.category.title,
        occupies_seat=occupies_seat,
        seat_label=seat_label,
        user=user,
    )
