"""
byceps.services.shop.order.actions.award_badge
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ....user_badge.models.awarding import BadgeAwardingTuple
from ....user_badge.models.badge import BadgeID
from ....user_badge import service as badge_service

from ...article.models.article import ArticleNumber

from .. import event_service
from ..models.order import OrderID, OrderTuple
from ..models.order_action import Parameters


def award_badge(order: OrderTuple, article_number: ArticleNumber,
                quantity: int, parameters: Parameters) -> None:
    """Award badge to user."""
    badge_id = parameters['badge_id']
    user_id = order.placed_by_id

    _verify_badge_id(badge_id)

    for _ in range(quantity):
        awarding = badge_service.award_badge_to_user(badge_id, user_id)

        _create_order_event(order.id, awarding)


def _verify_badge_id(badge_id: BadgeID) -> None:
    """Raise exception if no badge with that ID is known."""
    badge = badge_service.find_badge(badge_id)

    if badge is None:
        raise ValueError('Unknown badge ID "{}".'.format(badge_id))


def _create_order_event(order_id: OrderID, awarding: BadgeAwardingTuple
                       ) -> None:
    event_type = 'badge-awarded'
    data = {
        'awarding_id': str(awarding.id),
        'badge_id': str(awarding.badge_id),
        'recipient_id': str(awarding.user_id),
    }

    event_service.create_event(event_type, order_id, data)
