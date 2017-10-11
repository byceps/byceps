"""
byceps.services.shop.order.actions.revoke_tickets
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import Set

from ....ticketing.models.ticket import Ticket, TicketID
from ....ticketing import ticket_service

from ...article.models.article import ArticleNumber

from .. import event_service
from ..models.order import OrderID, OrderTuple
from ..models.order_action import Parameters


def revoke_tickets(order: OrderTuple, article_number: ArticleNumber,
                   quantity: int, parameters: Parameters) -> None:
    """Revoke tickets."""
    ticket_ids = _get_ticket_ids(order.id)
        
    ticket_service.revoke_tickets(ticket_ids)

    _create_order_events(order.id, ticket_ids)


def _get_ticket_ids(order_id: OrderID) -> Set[TicketID]:
    event_type = 'ticket-created'

    events = event_service.find_events(order_id, event_type)

    return {event.data['ticket_id'] for event in events}


def _create_order_events(order_id: OrderID, ticket_ids: Set[TicketID]) -> None:
    tickets = ticket_service.find_tickets(ticket_ids)

    event_type = 'ticket-revoked'

    datas = [
        {
            'ticket_id': str(ticket.id),
            'ticket_code': str(ticket.code),
        }
        for ticket in tickets
    ]

    event_service.create_events(event_type, order_id, datas)
