"""
byceps.services.ticketing.ticket_bundle_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import Optional, Sequence

from ...database import db
from ...typing import UserID

from ..shop.order.transfer.models import OrderNumber

from .models.ticket import Ticket as DbTicket
from .models.ticket_bundle import TicketBundle as DbTicketBundle
from .ticket_creation_service import build_tickets
from .ticket_revocation_service import \
    _build_ticket_revoked_event as build_ticket_revoked_event
from .transfer.models import TicketBundleID, TicketCategoryID


def create_bundle(category_id: TicketCategoryID, ticket_quantity: int,
                  owned_by_id: UserID,
                  *, order_number: Optional[OrderNumber]=None
                 ) -> DbTicketBundle:
    """Create a ticket bundle and the given quantity of tickets."""
    if ticket_quantity < 1:
        raise ValueError('Ticket quantity must be positive.')

    bundle = DbTicketBundle(category_id, ticket_quantity, owned_by_id)
    db.session.add(bundle)

    tickets = list(build_tickets(category_id, owned_by_id, ticket_quantity,
                                 bundle=bundle, order_number=order_number))
    db.session.add_all(tickets)

    db.session.commit()

    return bundle


def revoke_bundle(bundle_id: TicketBundleID, initiator_id: UserID,
                  *, reason: Optional[str]=None) -> None:
    """Revoke the tickets included in this bundle."""
    bundle = find_bundle(bundle_id)

    if bundle is None:
        raise ValueError('Unknown ticket bundle ID.')

    for ticket in bundle.tickets:
        ticket.revoked = True

        event = build_ticket_revoked_event(ticket.id, initiator_id, reason)
        db.session.add(event)

    db.session.commit()


def find_bundle(bundle_id: TicketBundleID) -> Optional[DbTicketBundle]:
    """Return the ticket bundle with that id, or `None` if not found."""
    return DbTicketBundle.query.get(bundle_id)


def find_tickets_for_bundle(bundle_id: TicketBundleID) -> Sequence[DbTicket]:
    """Return all tickets included in this bundle."""
    return DbTicket.query \
        .filter(DbTicket.bundle_id == bundle_id) \
        .all()
