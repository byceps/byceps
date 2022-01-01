"""
byceps.services.ticketing.ticket_bundle_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Optional, Sequence

from sqlalchemy import select
from tenacity import retry, retry_if_exception_type, stop_after_attempt

from ...database import db, paginate, Pagination
from ...typing import PartyID, UserID

from ..shop.order.transfer.number import OrderNumber

from .dbmodels.category import Category as DbCategory
from .dbmodels.ticket import Ticket as DbTicket
from .dbmodels.ticket_bundle import TicketBundle as DbTicketBundle
from .ticket_creation_service import build_tickets, TicketCreationFailed
from .ticket_revocation_service import build_ticket_revoked_log_entry
from .transfer.models import TicketBundleID, TicketCategoryID


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

    bundle = DbTicketBundle(
        party_id, category_id, ticket_quantity, owned_by_id, label=label
    )
    db.session.add(bundle)

    tickets = list(
        build_tickets(
            party_id,
            category_id,
            owned_by_id,
            ticket_quantity,
            bundle=bundle,
            order_number=order_number,
            used_by_id=used_by_id,
        )
    )
    db.session.add_all(tickets)

    db.session.commit()

    return bundle


def revoke_bundle(
    bundle_id: TicketBundleID,
    initiator_id: UserID,
    *,
    reason: Optional[str] = None,
) -> None:
    """Revoke the tickets included in this bundle."""
    bundle = find_bundle(bundle_id)

    if bundle is None:
        raise ValueError('Unknown ticket bundle ID.')

    for ticket in bundle.tickets:
        ticket.revoked = True

        log_entry = build_ticket_revoked_log_entry(
            ticket.id, initiator_id, reason
        )
        db.session.add(log_entry)

    db.session.commit()


def delete_bundle(bundle_id: TicketBundleID) -> None:
    """Delete a bundle and the tickets assigned to it."""
    bundle = find_bundle(bundle_id)

    if bundle is None:
        raise ValueError('Unknown ticket bundle ID.')

    db.session.query(DbTicket) \
        .filter_by(bundle_id=bundle_id) \
        .delete()

    db.session.query(DbTicketBundle) \
        .filter_by(id=bundle_id) \
        .delete()

    db.session.commit()


def find_bundle(bundle_id: TicketBundleID) -> Optional[DbTicketBundle]:
    """Return the ticket bundle with that id, or `None` if not found."""
    return db.session.get(DbTicketBundle, bundle_id)


def find_tickets_for_bundle(bundle_id: TicketBundleID) -> Sequence[DbTicket]:
    """Return all tickets included in this bundle."""
    return db.session \
        .query(DbTicket) \
        .filter(DbTicket.bundle_id == bundle_id) \
        .all()


def get_bundles_for_party_paginated(
    party_id: PartyID, page: int, per_page: int
) -> Pagination:
    """Return the party's ticket bundles to show on the specified page."""
    items_query = select(DbTicketBundle) \
        .join(DbCategory) \
        .filter(DbCategory.party_id == party_id) \
        .options(
            db.joinedload(DbTicketBundle.ticket_category),
            db.joinedload(DbTicketBundle.owned_by),
        ) \
        .order_by(DbTicketBundle.created_at.desc())

    count_query = select(db.func.count(DbTicketBundle.id)) \
        .join(DbCategory) \
        .filter(DbCategory.party_id == party_id)

    return paginate(
        items_query, count_query, page, per_page, scalar_result=True
    )
