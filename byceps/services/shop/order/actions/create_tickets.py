"""
byceps.services.shop.order.actions.create_tickets
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ....ticketing import ticket_service

from ...article.models.article import ArticleNumber

from ..models.order import OrderTuple
from ..models.order_action import Parameters


def create_tickets(order: OrderTuple, article_number: ArticleNumber,
                   quantity: int, parameters: Parameters) -> None:
    """Create tickets."""
    category_id = parameters['category_id']
    owned_by_id = order.placed_by_id
    order_number = order.order_number

    tickets = ticket_service.create_tickets(category_id, owned_by_id, quantity,
                                            order_number=order_number)
