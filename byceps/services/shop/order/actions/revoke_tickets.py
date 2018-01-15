"""
byceps.services.shop.order.actions.revoke_tickets
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


def revoke_tickets(order: OrderTuple, article_number: ArticleNumber,
                   quantity: int, parameters: Parameters) -> None:
    """Revoke tickets."""
    tickets = ticket_service.find_tickets_created_by_order(order.order_number)

    ticket_ids = {t.id for t in tickets}
    ticket_service.revoke_tickets(ticket_ids)

    _create_order_events(order.id, tickets)


def _create_order_events(order_id: OrderID, tickets: Sequence[Ticket]) -> None:
    event_type = 'ticket-revoked'

    datas = [
        {
            'ticket_id': str(ticket.id),
            'ticket_code': ticket.code,
        }
        for ticket in tickets
    ]

    event_service.create_events(event_type, order_id, datas)
