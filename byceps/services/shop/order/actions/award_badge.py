"""
byceps.services.shop.order.actions.award_badge
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import Any, Dict

from .....util.iterables import find

from ....user_badge.models.badge import BadgeID
from ....user_badge import service as badge_service

from ...article.models.article import ArticleNumber

from ..models.order import Order


def award_badge(order: Order, article_number: ArticleNumber,
                parameters: Dict[str, Any]) -> None:
    """Award badge to user."""
    badge_id = parameters['badge_id']
    user_id = order.placed_by_id

    verify_badge_id(badge_id)

    quantity = get_article_quantity(article_number, order)

    for _ in range(quantity):
        badge_service.award_badge_to_user(badge_id, user_id)


def verify_badge_id(badge_id: BadgeID) -> None:
    """Raise exception if no badge with that ID is known."""
    badge = badge_service.find_badge(badge_id)

    if badge is None:
        raise ValueError('Unknown badge ID "{}".'.format(badge_id))


def get_article_quantity(article_number: ArticleNumber, order: Order) -> int:
    """Return the quantity of the article in that order."""
    relevant_order_item = find(
        lambda item: item.article_number == article_number, order.items)

    if relevant_order_item is None:
        raise Exception('No item with article number "{}" found in order "{}".'
                        .format(article_number, order.order_number))

    return relevant_order_item.quantity
