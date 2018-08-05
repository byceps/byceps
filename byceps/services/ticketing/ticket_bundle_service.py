"""
byceps.services.ticketing.ticket_bundle_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import Optional, Sequence

from ...database import db
from ...typing import UserID

from ..shop.order.transfer.models import OrderNumber

from .models.ticket import Ticket
from .models.ticket_bundle import TicketBundle
from .ticket_creation_service import build_tickets
from .ticket_revocation_service import \
    _build_ticket_revoked_event as build_ticket_revoked_event
from .transfer.models import TicketBundleID, TicketCategoryID


def create_bundle(category_id: TicketCategoryID, ticket_quantity: int,
                  owned_by_id: UserID,
                  *, order_number: Optional[OrderNumber]=None
                 ) -> TicketBundle:
    """Create a ticket bundle and the given quantity of tickets."""
    if ticket_quantity < 1:
        raise ValueError('Ticket quantity must be positive.')

    bundle = TicketBundle(category_id, ticket_quantity, owned_by_id)
    db.session.add(bundle)

    tickets = list(build_tickets(category_id, owned_by_id, ticket_quantity,
                                 bundle=bundle, order_number=order_number))
    db.session.add_all(tickets)

    db.session.commit()

    return bundle


def revoke_bundle(bundle_id: TicketBundleID, *,
                  initiator_id: Optional[UserID]=None,
                  reason: Optional[str]=None
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


def find_bundle(bundle_id: TicketBundleID) -> Optional[TicketBundle]:
    """Return the ticket bundle with that id, or `None` if not found."""
    return TicketBundle.query.get(bundle_id)


def find_tickets_for_bundle(bundle_id: TicketBundleID) -> Sequence[Ticket]:
    """Return all tickets included in this bundle."""
    return Ticket.query \
        .filter(Ticket.bundle_id == bundle_id) \
        .all()
