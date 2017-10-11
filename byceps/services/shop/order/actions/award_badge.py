"""
byceps.services.shop.order.actions.award_badge
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ....user_badge.models.badge import BadgeID
from ....user_badge import service as badge_service

from ...article.models.article import ArticleNumber

from ..models.order import OrderTuple
from ..models.order_action import Parameters


def award_badge(order: OrderTuple, article_number: ArticleNumber,
                quantity: int, parameters: Parameters) -> None:
    """Award badge to user."""
    badge_id = parameters['badge_id']
    user_id = order.placed_by_id

    _verify_badge_id(badge_id)

    for _ in range(quantity):
        badge_service.award_badge_to_user(badge_id, user_id)


def _verify_badge_id(badge_id: BadgeID) -> None:
    """Raise exception if no badge with that ID is known."""
    badge = badge_service.find_badge(badge_id)

    if badge is None:
        raise ValueError('Unknown badge ID "{}".'.format(badge_id))
