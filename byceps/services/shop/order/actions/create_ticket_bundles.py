"""
byceps.services.shop.order.actions.create_ticket_bundles
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from .....typing import UserID

from ....ticketing.models.ticket_bundle import TicketBundle
from ....ticketing import ticket_bundle_service

from ...article.transfer.models import ArticleNumber

from .. import event_service
from ..models.order_action import Parameters
from ..transfer.models import Order, OrderID

from ._ticketing import create_tickets_sold_event, send_tickets_sold_event


def create_ticket_bundles(
    order: Order,
    article_number: ArticleNumber,
    bundle_quantity: int,
    initiator_id: UserID,
    parameters: Parameters,
) -> None:
    """Create ticket bundles."""
    category_id = parameters['category_id']
    ticket_quantity = parameters['ticket_quantity']
    owned_by_id = order.placed_by_id
    order_number = order.order_number

    for _ in range(bundle_quantity):
        bundle = ticket_bundle_service.create_bundle(
            category_id,
            ticket_quantity,
            owned_by_id,
            order_number=order_number,
            used_by_id=owned_by_id,
        )

        _create_order_event(order.id, bundle)

    tickets_sold_event = create_tickets_sold_event(
        initiator_id, owned_by_id, ticket_quantity
    )
    send_tickets_sold_event(tickets_sold_event)


def _create_order_event(order_id: OrderID, ticket_bundle: TicketBundle) -> None:
    event_type = 'ticket-bundle-created'

    data = {
        'ticket_bundle_id': str(ticket_bundle.id),
        'ticket_bundle_category_id': str(ticket_bundle.ticket_category_id),
        'ticket_bundle_ticket_quantity': ticket_bundle.ticket_quantity,
        'ticket_bundle_owner_id': str(ticket_bundle.owned_by_id),
    }

    event_service.create_event(event_type, order_id, data)
