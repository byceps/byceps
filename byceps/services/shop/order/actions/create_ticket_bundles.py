"""
byceps.services.shop.order.actions.create_ticket_bundles
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ....ticketing.models.ticket_bundle import TicketBundle
from ....ticketing import ticket_bundle_service

from ...article.models.article import ArticleNumber

from .. import event_service
from ..models.order import OrderID, OrderTuple
from ..models.order_action import Parameters


def create_ticket_bundles(order: OrderTuple, article_number: ArticleNumber,
                          bundle_quantity: int, parameters: Parameters) -> None:
    """Create ticket bundles."""
    category_id = parameters['category_id']
    ticket_quantity = parameters['ticket_quantity']
    owned_by_id = order.placed_by_id
    order_number = order.order_number

    for _ in range(bundle_quantity):
        bundle = ticket_bundle_service.create_bundle(
            category_id, ticket_quantity, owned_by_id,
            order_number=order_number)

        for ticket in bundle.tickets:
            ticket.used_by_id = owned_by_id

        _create_order_event(order.id, bundle)


def _create_order_event(order_id: OrderID, ticket_bundle: TicketBundle) -> None:
    event_type = 'ticket-bundle-created'

    data = {
        'ticket_bundle_id': str(ticket_bundle.id),
        'ticket_bundle_category_id': str(ticket_bundle.ticket_category_id),
        'ticket_bundle_ticket_quantity': ticket_bundle.ticket_quantity,
        'ticket_bundle_owner_id': str(ticket_bundle.owned_by_id),
    }

    event_service.create_event(event_type, order_id, data)
