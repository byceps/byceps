"""
byceps.services.shop.order.actions.create_tickets
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Sequence

from .....typing import UserID

from ....ticketing.models.ticket import Ticket
from ....ticketing import ticket_creation_service

from ...article.transfer.models import ArticleNumber

from .. import event_service
from ..models.order_action import Parameters
from ..transfer.models import Order, OrderID

from ._ticketing import create_tickets_sold_event, send_tickets_sold_event


def create_tickets(
    order: Order,
    article_number: ArticleNumber,
    quantity: int,
    initiator_id: UserID,
    parameters: Parameters,
) -> None:
    """Create tickets."""
    category_id = parameters['category_id']
    owned_by_id = order.placed_by_id
    order_number = order.order_number

    tickets = ticket_creation_service.create_tickets(
        category_id,
        owned_by_id,
        quantity,
        order_number=order_number,
        used_by_id=owned_by_id,
    )

    _create_order_events(order.id, tickets)

    tickets_sold_event = create_tickets_sold_event(
        order.id, initiator_id, category_id, owned_by_id, quantity
    )
    send_tickets_sold_event(tickets_sold_event)


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
