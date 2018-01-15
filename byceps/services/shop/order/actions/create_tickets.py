"""
byceps.services.shop.order.actions.create_tickets
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import Sequence

from ....ticketing.models.ticket import Ticket
from ....ticketing import ticket_service

from ...article.models.article import ArticleNumber

from .. import event_service
from ..models.order import OrderID, OrderTuple
from ..models.order_action import Parameters


def create_tickets(order: OrderTuple, article_number: ArticleNumber,
                   quantity: int, parameters: Parameters) -> None:
    """Create tickets."""
    category_id = parameters['category_id']
    owned_by_id = order.placed_by_id
    order_number = order.order_number

    tickets = ticket_service.create_tickets(category_id, owned_by_id, quantity,
                                            order_number=order_number)

    for ticket in tickets:
        ticket.used_by_id = owned_by_id

    _create_order_events(order.id, tickets)


def _create_order_events(order_id: OrderID, tickets: Sequence[Ticket]) -> None:
    event_type = 'ticket-created'

    datas = [
        {
            'ticket_id': str(ticket.id),
            'ticket_code': ticket.code,
            'ticket_category_id': str(ticket.category_id),
            'ticket_owner_id': str(ticket.owned_by_id),
        }
        for ticket in tickets
    ]

    event_service.create_events(event_type, order_id, datas)
