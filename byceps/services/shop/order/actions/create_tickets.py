"""
byceps.services.shop.order.actions.create_tickets
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Sequence

from .....typing import UserID

from ....ticketing.dbmodels.ticket import Ticket
from ....ticketing import (
    category_service as ticket_category_service,
    ticket_creation_service,
)

from ...article.transfer.models import ArticleNumber

from .. import log_service
from ..transfer.models.action import ActionParameters
from ..transfer.models.order import Order, OrderID

from ._ticketing import create_tickets_sold_event, send_tickets_sold_event


def create_tickets(
    order: Order,
    article_number: ArticleNumber,
    quantity: int,
    initiator_id: UserID,
    parameters: ActionParameters,
) -> None:
    """Create tickets."""
    category_id = parameters['category_id']
    owned_by_id = order.placed_by_id
    order_number = order.order_number

    category = ticket_category_service.get_category(category_id)

    tickets = ticket_creation_service.create_tickets(
        category.party_id,
        category_id,
        owned_by_id,
        quantity,
        order_number=order_number,
        used_by_id=owned_by_id,
    )

    _create_order_log_entries(order.id, tickets)

    tickets_sold_event = create_tickets_sold_event(
        order.id, initiator_id, category_id, owned_by_id, quantity
    )
    send_tickets_sold_event(tickets_sold_event)


def _create_order_log_entries(
    order_id: OrderID, tickets: Sequence[Ticket]
) -> None:
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

    log_service.create_entries(event_type, order_id, datas)
