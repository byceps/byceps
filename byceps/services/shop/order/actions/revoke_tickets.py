"""
byceps.services.shop.order.actions.revoke_tickets
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Sequence

from .....typing import UserID

from ....ticketing.dbmodels.ticket import Ticket
from ....ticketing import ticket_revocation_service, ticket_service

from ...article.transfer.models import ArticleNumber

from .. import log_service
from ..transfer.action import ActionParameters
from ..transfer.order import Order, OrderID


def revoke_tickets(
    order: Order,
    article_number: ArticleNumber,
    quantity: int,
    initiator_id: UserID,
    parameters: ActionParameters,
) -> None:
    """Revoke all tickets in this order."""
    tickets = ticket_service.find_tickets_created_by_order(order.order_number)

    ticket_ids = {t.id for t in tickets}
    ticket_revocation_service.revoke_tickets(ticket_ids, initiator_id)

    _create_order_log_entries(order.id, tickets, initiator_id)


def _create_order_log_entries(
    order_id: OrderID, tickets: Sequence[Ticket], initiator_id: UserID
) -> None:
    event_type = 'ticket-revoked'

    datas = [
        {
            'ticket_id': str(ticket.id),
            'ticket_code': ticket.code,
            'initiator_id': str(initiator_id),
        }
        for ticket in tickets
    ]

    log_service.create_entries(event_type, order_id, datas)
