"""
byceps.services.ticketing.ticket_bundle_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import Optional, Sequence

from tenacity import retry, retry_if_exception_type, stop_after_attempt

from ...database import db, Pagination
from ...typing import PartyID, UserID

from ..shop.order.transfer.models import OrderNumber

from .models.category import Category as DbCategory
from .models.ticket import Ticket as DbTicket
from .models.ticket_bundle import TicketBundle as DbTicketBundle
from .ticket_creation_service import build_tickets, TicketCreationFailed
from .ticket_revocation_service import (
    _build_ticket_revoked_event as build_ticket_revoked_event,
)
from .transfer.models import TicketBundleID, TicketCategoryID


@retry(
    reraise=True,
    retry=retry_if_exception_type(TicketCreationFailed),
    stop=stop_after_attempt(5),
)
def create_bundle(
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
        category_id, ticket_quantity, owned_by_id, label=label
    )
    db.session.add(bundle)

    tickets = list(
        build_tickets(
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

        event = build_ticket_revoked_event(ticket.id, initiator_id, reason)
        db.session.add(event)

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
    return DbTicketBundle.query.get(bundle_id)


def find_tickets_for_bundle(bundle_id: TicketBundleID) -> Sequence[DbTicket]:
    """Return all tickets included in this bundle."""
    return DbTicket.query \
        .filter(DbTicket.bundle_id == bundle_id) \
        .all()


def get_bundles_for_party_paginated(
    party_id: PartyID, page: int, per_page: int
) -> Pagination:
    """Return the party's ticket bundles to show on the specified page."""
    return DbTicketBundle.query \
        .join(DbCategory) \
        .filter(DbCategory.party_id == party_id) \
        .options(
            db.joinedload('ticket_category'),
            db.joinedload('owned_by'),
        ) \
        .order_by(DbTicketBundle.created_at.desc()) \
        .paginate(page, per_page)
