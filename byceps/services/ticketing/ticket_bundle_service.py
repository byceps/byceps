"""
byceps.services.ticketing.ticket_bundle_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Optional

from sqlalchemy import delete, select
from tenacity import retry, retry_if_exception_type, stop_after_attempt

from ...database import db, paginate, Pagination
from ...typing import PartyID, UserID

from ..seating import seat_group_service
from ..shop.order.models.number import OrderNumber

from .dbmodels.category import DbTicketCategory
from .dbmodels.ticket import DbTicket
from .dbmodels.ticket_bundle import DbTicketBundle
from .models.ticket import TicketBundleID, TicketCategoryID
from .ticket_creation_service import build_tickets, TicketCreationFailed
from .ticket_revocation_service import build_ticket_revoked_log_entry


@retry(
    reraise=True,
    retry=retry_if_exception_type(TicketCreationFailed),
    stop=stop_after_attempt(5),
)
def create_bundle(
    party_id: PartyID,
    category_id: TicketCategoryID,
    ticket_quantity: int,
    owned_by_id: UserID,
    *,
    label: Optional[str] = None,
    order_number: Optional[OrderNumber] = None,
    used_by_id: Optional[UserID] = None,
) -> DbTicketBundle:
    """Create a ticket bundle and the given quantity of tickets."""
    if ticket_quantity < 1:
        raise ValueError('Ticket quantity must be positive.')

    db_bundle = DbTicketBundle(
        party_id, category_id, ticket_quantity, owned_by_id, label=label
    )
    db.session.add(db_bundle)

    db_tickets = list(
        build_tickets(
            party_id,
            category_id,
            owned_by_id,
            ticket_quantity,
            bundle=db_bundle,
            order_number=order_number,
            used_by_id=used_by_id,
        )
    )
    db.session.add_all(db_tickets)

    db.session.commit()

    return db_bundle


def revoke_bundle(
    bundle_id: TicketBundleID,
    initiator_id: UserID,
    *,
    reason: Optional[str] = None,
) -> None:
    """Revoke the tickets included in this bundle."""
    db_bundle = get_bundle(bundle_id)

    seat_group_id = (
        seat_group_service.find_seat_group_occupied_by_ticket_bundle(
            db_bundle.id
        )
    )
    if seat_group_id is not None:
        seat_group_service.release_seat_group(seat_group_id)

    for db_ticket in db_bundle.tickets:
        db_ticket.revoked = True

        db_log_entry = build_ticket_revoked_log_entry(
            db_ticket.id, initiator_id, reason
        )
        db.session.add(db_log_entry)

    db.session.commit()


def delete_bundle(bundle_id: TicketBundleID) -> None:
    """Delete a bundle and the tickets assigned to it."""
    db_bundle = get_bundle(bundle_id)

    db.session.execute(delete(DbTicket).filter_by(bundle_id=db_bundle.id))
    db.session.execute(delete(DbTicketBundle).filter_by(id=db_bundle.id))
    db.session.commit()


def find_bundle(bundle_id: TicketBundleID) -> Optional[DbTicketBundle]:
    """Return the ticket bundle with that id, or `None` if not found."""
    return db.session.get(DbTicketBundle, bundle_id)


def get_bundle(bundle_id: TicketBundleID) -> DbTicketBundle:
    """Return the ticket bundle with that id, or raise an exception."""
    db_bundle = find_bundle(bundle_id)

    if db_bundle is None:
        raise ValueError(f'Unknown ticket bundle ID "{bundle_id}"')

    return db_bundle


def get_tickets_for_bundle(bundle_id: TicketBundleID) -> list[DbTicket]:
    """Return all tickets included in this bundle."""
    return db.session.scalars(
        select(DbTicket).filter(DbTicket.bundle_id == bundle_id)
    ).all()


def get_bundles_for_party_paginated(
    party_id: PartyID, page: int, per_page: int
) -> Pagination:
    """Return the party's ticket bundles to show on the specified page."""
    items_query = (
        select(DbTicketBundle)
        .join(DbTicketCategory)
        .filter(DbTicketCategory.party_id == party_id)
        .options(
            db.joinedload(DbTicketBundle.ticket_category),
            db.joinedload(DbTicketBundle.owned_by),
        )
        .order_by(DbTicketBundle.created_at.desc())
    )

    count_query = (
        select(db.func.count(DbTicketBundle.id))
        .join(DbTicketCategory)
        .filter(DbTicketCategory.party_id == party_id)
    )

    return paginate(
        items_query, count_query, page, per_page, scalar_result=True
    )
