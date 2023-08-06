"""
byceps.services.ticketing.ticket_bundle_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import delete, select
from tenacity import retry, retry_if_exception_type, stop_after_attempt

from byceps.database import db, paginate, Pagination
from byceps.services.seating import seat_group_service
from byceps.services.shop.order.models.number import OrderNumber
from byceps.services.user.models.user import User
from byceps.typing import PartyID

from .dbmodels.category import DbTicketCategory
from .dbmodels.ticket import DbTicket
from .dbmodels.ticket_bundle import DbTicketBundle
from .models.ticket import TicketBundleID, TicketCategoryID
from .ticket_creation_service import build_tickets, TicketCreationFailedError
from .ticket_revocation_service import build_ticket_revoked_log_entry


@retry(
    reraise=True,
    retry=retry_if_exception_type(TicketCreationFailedError),
    stop=stop_after_attempt(5),
)
def create_bundle(
    party_id: PartyID,
    category_id: TicketCategoryID,
    ticket_quantity: int,
    owner: User,
    *,
    label: str | None = None,
    order_number: OrderNumber | None = None,
    user: User | None = None,
) -> DbTicketBundle:
    """Create a ticket bundle and the given quantity of tickets."""
    if ticket_quantity < 1:
        raise ValueError('Ticket quantity must be positive.')

    db_bundle = DbTicketBundle(
        party_id, category_id, ticket_quantity, owner.id, label=label
    )
    db.session.add(db_bundle)

    db_tickets = list(
        build_tickets(
            party_id,
            category_id,
            owner,
            ticket_quantity,
            bundle=db_bundle,
            order_number=order_number,
            user=user,
        )
    )
    db.session.add_all(db_tickets)

    db.session.commit()

    return db_bundle


def revoke_bundle(
    bundle_id: TicketBundleID,
    initiator: User,
    *,
    reason: str | None = None,
) -> None:
    """Revoke the tickets included in this bundle."""
    db_bundle = get_bundle(bundle_id)

    db_bundle.revoked = True

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


def get_bundles_for_party_paginated(
    party_id: PartyID, page: int, per_page: int
) -> Pagination:
    """Return the party's ticket bundles to show on the specified page."""
    stmt = (
        select(DbTicketBundle)
        .join(DbTicketCategory)
        .filter(DbTicketCategory.party_id == party_id)
        .options(
            db.joinedload(DbTicketBundle.ticket_category),
            db.joinedload(DbTicketBundle.owned_by),
        )
        .order_by(DbTicketBundle.created_at.desc())
    )

    return paginate(stmt, page, per_page)
