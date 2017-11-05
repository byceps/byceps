"""
byceps.services.shop.order.actions.revoke_tickets
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import Sequence

from ....ticketing.models.ticket import Ticket
from ....ticketing import event_service as ticket_event_service, ticket_service

from ...article.models.article import ArticleNumber

from .. import event_service
from ..models.order import OrderID, OrderTuple
from ..models.order_action import Parameters
from ..models.order_event import OrderEventData


def revoke_tickets(order: OrderTuple, article_number: ArticleNumber,
                   quantity: int, parameters: Parameters) -> None:
    """Revoke tickets."""
    tickets = ticket_service.find_tickets_created_by_order(order.order_number)

    ticket_ids = {t.id for t in tickets}
    ticket_service.revoke_tickets(ticket_ids)

    _create_ticket_events(tickets)

    _create_order_events(order.id, tickets)


def _create_ticket_events(tickets: Sequence[Ticket]) -> None:
    event_type = 'ticket-revoked'

    for ticket in tickets:
        data = {}  # type: OrderEventData
        ticket_event_service.create_event(event_type, ticket.id, data)


def _create_order_events(order_id: OrderID, tickets: Sequence[Ticket]) -> None:
    event_type = 'ticket-revoked'

    datas = [
        {
            'ticket_id': str(ticket.id),
            'ticket_code': str(ticket.code),
        }
        for ticket in tickets
    ]

    event_service.create_events(event_type, order_id, datas)
