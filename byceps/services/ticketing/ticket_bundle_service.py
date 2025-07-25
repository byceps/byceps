"""
byceps.services.ticketing.ticket_bundle_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections.abc import Sequence
from datetime import datetime

from sqlalchemy import delete, select, Select
from tenacity import retry, retry_if_exception_type, stop_after_attempt

from byceps.database import db, paginate, Pagination
from byceps.services.party.models import PartyID
from byceps.services.seating import seat_group_service
from byceps.services.seating.models import SeatGroupID
from byceps.services.shop.order.models.number import OrderNumber
from byceps.services.user import user_service
from byceps.services.user.models.user import User
from byceps.util.uuid import generate_uuid7

from . import ticket_category_service
from .dbmodels.category import DbTicketCategory
from .dbmodels.ticket import DbTicket
from .dbmodels.ticket_bundle import DbTicketBundle
from .models.ticket import (
    TicketBundle,
    TicketBundleID,
    TicketCategory,
    TicketID,
)
from .ticket_creation_service import build_tickets, TicketCreationFailedError
from .ticket_revocation_service import build_ticket_revoked_log_entry


@retry(
    reraise=True,
    retry=retry_if_exception_type(TicketCreationFailedError),
    stop=stop_after_attempt(5),
)
def create_bundle(
    category: TicketCategory,
    ticket_quantity: int,
    owner: User,
    *,
    label: str | None = None,
    order_number: OrderNumber | None = None,
    user: User | None = None,
) -> TicketBundle:
    """Create a ticket bundle and the given quantity of tickets."""
    if ticket_quantity < 1:
        raise ValueError('Ticket quantity must be positive.')

    bundle_id = TicketBundleID(generate_uuid7())
    created_at = datetime.utcnow()

    db_bundle = DbTicketBundle(
        bundle_id,
        created_at,
        category,
        ticket_quantity,
        owner.id,
        label=label,
    )
    db.session.add(db_bundle)

    db_tickets = list(
        build_tickets(
            category,
            owner,
            ticket_quantity,
            bundle_id=bundle_id,
            order_number=order_number,
            user=user,
        )
    )
    db.session.add_all(db_tickets)

    db.session.commit()

    ticket_ids = {db_ticket.id for db_ticket in db_tickets}

    bundle = TicketBundle(
        id=bundle_id,
        created_at=created_at,
        party_id=category.party_id,
        ticket_category=category,
        ticket_quantity=ticket_quantity,
        owned_by=owner,
        seats_managed_by=None,
        users_managed_by=None,
        label=label,
        revoked=False,
        ticket_ids=ticket_ids,
        occupied_seat_group_id=_find_occupied_seat_group_id(db_bundle),
    )

    return bundle


def revoke_bundle(
    bundle_id: TicketBundleID,
    initiator: User,
    *,
    reason: str | None = None,
) -> None:
    """Revoke the tickets included in this bundle."""
    db_bundle = get_bundle(bundle_id)

    db_bundle.revoked = True

    seat_group_id = seat_group_service.find_group_occupied_by_ticket_bundle(
        db_bundle.id
    )
    if seat_group_id is not None:
        release_result = seat_group_service.release_group(
            seat_group_id, initiator
        )
        if release_result.is_err():
            error_msg = release_result.unwrap_err().message
            raise ValueError(
                f'Could not release seat group {seat_group_id}: {error_msg}'
            )

    for db_ticket in db_bundle.tickets:
        db_ticket.revoked = True

        db_log_entry = build_ticket_revoked_log_entry(
            db_ticket.id, initiator.id, reason
        )
        db.session.add(db_log_entry)

    db.session.commit()


def delete_bundle(bundle_id: TicketBundleID) -> None:
    """Delete a bundle and the tickets assigned to it."""
    db_bundle = get_bundle(bundle_id)

    db.session.execute(delete(DbTicket).filter_by(bundle_id=db_bundle.id))
    db.session.execute(delete(DbTicketBundle).filter_by(id=db_bundle.id))
    db.session.commit()


def find_bundle(bundle_id: TicketBundleID) -> DbTicketBundle | None:
    """Return the ticket bundle with that id, or `None` if not found."""
    return db.session.get(DbTicketBundle, bundle_id)


def get_bundle(bundle_id: TicketBundleID) -> DbTicketBundle:
    """Return the ticket bundle with that id, or raise an exception."""
    db_bundle = find_bundle(bundle_id)

    if db_bundle is None:
        raise ValueError(f'Unknown ticket bundle ID "{bundle_id}"')

    return db_bundle


def get_tickets_for_bundle(bundle_id: TicketBundleID) -> Sequence[DbTicket]:
    """Return all tickets included in this bundle."""
    return db.session.scalars(
        select(DbTicket).filter(DbTicket.bundle_id == bundle_id)
    ).all()


def get_bundles_for_party(party_id: PartyID) -> list[TicketBundle]:
    """Return the party's ticket bundles."""
    stmt = _get_bundles_for_party_stmt(party_id)
    db_bundles = db.session.scalars(stmt).all()

    return [db_entity_to_ticket_bundle(db_bundle) for db_bundle in db_bundles]


def get_bundles_for_party_paginated(
    party_id: PartyID, page: int, per_page: int
) -> Pagination:
    """Return the party's ticket bundles to show on the specified page."""
    stmt = _get_bundles_for_party_stmt(party_id)
    return paginate(stmt, page, per_page)


def _get_bundles_for_party_stmt(party_id: PartyID) -> Select:
    return (
        select(DbTicketBundle)
        .join(DbTicketCategory)
        .filter(DbTicketCategory.party_id == party_id)
        .options(
            db.joinedload(DbTicketBundle.ticket_category),
            db.joinedload(DbTicketBundle.owned_by),
        )
        .order_by(DbTicketBundle.created_at.desc())
    )


def db_entity_to_ticket_bundle(db_bundle: DbTicketBundle) -> TicketBundle:
    ticket_category = ticket_category_service.get_category(
        db_bundle.ticket_category_id
    )

    owner = user_service.get_user(db_bundle.owned_by.id)

    seats_manager = (
        user_service.get_user(db_bundle.seats_managed_by.id)
        if db_bundle.seats_managed_by
        else None
    )

    users_manager = (
        user_service.get_user(db_bundle.users_managed_by.id)
        if db_bundle.users_managed_by
        else None
    )

    ticket_ids = {db_ticket.id for db_ticket in db_bundle.tickets}

    return _db_entity_to_ticket_bundle(
        db_bundle,
        ticket_category,
        owner,
        seats_manager,
        users_manager,
        ticket_ids,
    )


def _db_entity_to_ticket_bundle(
    db_bundle: DbTicketBundle,
    ticket_category: TicketCategory,
    owner: User,
    seats_manager: User | None,
    users_manager: User | None,
    ticket_ids: set[TicketID],
) -> TicketBundle:
    return TicketBundle(
        id=db_bundle.id,
        created_at=db_bundle.created_at,
        party_id=db_bundle.party_id,
        ticket_category=ticket_category,
        ticket_quantity=db_bundle.ticket_quantity,
        owned_by=owner,
        seats_managed_by=seats_manager,
        users_managed_by=users_manager,
        label=db_bundle.label,
        revoked=db_bundle.revoked,
        ticket_ids=ticket_ids,
        occupied_seat_group_id=_find_occupied_seat_group_id(db_bundle),
    )


def _find_occupied_seat_group_id(
    db_bundle: DbTicketBundle,
) -> SeatGroupID | None:
    occupied_seat_group = db_bundle.occupied_seat_group
    return occupied_seat_group.id if occupied_seat_group else None
