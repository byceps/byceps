"""
byceps.services.seating.blueprints.admin.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass

from byceps.services.party.models import PartyID
from byceps.services.seating import seat_group_service
from byceps.services.seating.models import SeatGroup, SeatGroupID, SeatID
from byceps.services.ticketing import ticket_category_service, ticket_service
from byceps.services.ticketing.models.ticket import (
    TicketCategory,
    TicketCategoryID,
    TicketCode,
    TicketID,
)
from byceps.services.user import user_service
from byceps.services.user.models.user import User


@dataclass(frozen=True, kw_only=True)
class SeatGroupSeatTicketForAdmin:
    id: TicketID
    code: TicketCode
    owned_by: User
    used_by: User | None
    revoked: bool
    user_checked_in: bool


@dataclass(frozen=True, kw_only=True)
class SeatGroupSeatForAdmin:
    id: SeatID
    label: str | None
    occupied_by_ticket: SeatGroupSeatTicketForAdmin | None


@dataclass(frozen=True, kw_only=True)
class SeatGroupForAdmin:
    id: SeatGroupID
    ticket_category: TicketCategory
    seat_quantity: int
    title: str
    seats: list[SeatGroupSeatForAdmin]


def get_seat_groups_for_admin(party_id: PartyID) -> list[SeatGroupForAdmin]:
    groups = seat_group_service.get_groups_for_party(party_id)

    ticket_categories_by_id = _get_ticket_categories_by_id(party_id)
    tickets_for_admin_by_id = _get_tickets_for_admin_by_id(groups)

    return [
        SeatGroupForAdmin(
            id=group.id,
            ticket_category=ticket_categories_by_id[group.ticket_category_id],
            seat_quantity=group.seat_quantity,
            title=group.title,
            seats=[
                SeatGroupSeatForAdmin(
                    id=seat.id,
                    label=seat.label,
                    occupied_by_ticket=tickets_for_admin_by_id[
                        seat.occupied_by_ticket_id
                    ]
                    if seat.occupied_by_ticket_id
                    else None,
                )
                for seat in group.seats
            ],
        )
        for group in groups
    ]


def _get_ticket_categories_by_id(
    party_id: PartyID,
) -> dict[TicketCategoryID, TicketCategory]:
    ticket_categories = ticket_category_service.get_categories_for_party(
        party_id
    )
    return {c.id: c for c in ticket_categories}


def _get_tickets_for_admin_by_id(
    groups: list[SeatGroup],
) -> dict[TicketID, SeatGroupSeatTicketForAdmin]:
    ticket_ids = {
        seat.occupied_by_ticket_id
        for group in groups
        for seat in group.seats
        if seat.occupied_by_ticket_id
    }

    db_tickets = ticket_service.get_tickets(ticket_ids)

    ticket_owner_ids = {db_ticket.owned_by_id for db_ticket in db_tickets}
    ticket_user_ids = {
        db_ticket.used_by_id for db_ticket in db_tickets if db_ticket.used_by_id
    }

    users_by_id = user_service.get_users_for_admin_indexed_by_id(
        ticket_owner_ids | ticket_user_ids
    )

    return {
        db_ticket.id: SeatGroupSeatTicketForAdmin(
            id=db_ticket.id,
            code=TicketCode(db_ticket.code),
            owned_by=users_by_id[db_ticket.owned_by_id],
            used_by=users_by_id[db_ticket.used_by_id]
            if db_ticket.used_by_id
            else None,
            revoked=db_ticket.revoked,
            user_checked_in=db_ticket.user_checked_in,
        )
        for db_ticket in db_tickets
    }
