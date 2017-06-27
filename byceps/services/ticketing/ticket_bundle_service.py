"""
byceps.services.ticketing.ticket_bundle_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ...database import db
from ...typing import UserID

from ..seating.models.category import CategoryID

from .models.ticket_bundle import TicketBundle
from .ticket_service import build_tickets


def create_ticket_bundle(category_id: CategoryID, ticket_quantity: int,
                         owned_by_id: UserID) -> TicketBundle:
    """Create a ticket bundle and the given quantity of tickets."""
    if ticket_quantity < 1:
        raise ValueError('Ticket quantity must be positive.')

    bundle = TicketBundle(category_id, ticket_quantity, owned_by_id)
    db.session.add(bundle)

    tickets = list(build_tickets(category_id, owned_by_id, ticket_quantity,
                                 bundle=bundle))
    db.session.add_all(tickets)

    db.session.commit()

    return bundle


def delete_ticket_bundle(bundle: TicketBundle) -> None:
    """Delete the ticket bundle and the tickets associated with it."""
    for ticket in bundle.tickets:
        db.session.delete(ticket)

    db.session.delete(bundle)

    db.session.commit()
