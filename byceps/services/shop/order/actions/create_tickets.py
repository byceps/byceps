"""
byceps.services.shop.order.actions.create_tickets
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import Any, Dict

from .....util.iterables import find

from ....ticketing import ticket_service

from ...article.models.article import ArticleNumber

from ..models.order import Order


def create_tickets(order: Order, article_number: ArticleNumber,
                   parameters: Dict[str, Any]) -> None:
    """Create tickets."""
    category_id = parameters['category_id']
    owned_by_id = order.placed_by_id
    quantity = get_article_quantity(article_number, order)
    order_number = order.order_number

    tickets = ticket_service.create_tickets(category_id, owned_by_id, quantity,
                                            order_number=order_number)


def get_article_quantity(article_number: ArticleNumber, order: Order) -> int:
    """Return the quantity of the article in that order."""
    relevant_order_item = find(
        lambda item: item.article_number == article_number, order.items)

    if relevant_order_item is None:
        raise Exception('No item with article number "{}" found in order "{}".'
                        .format(article_number, order.order_number))

    return relevant_order_item.quantity
