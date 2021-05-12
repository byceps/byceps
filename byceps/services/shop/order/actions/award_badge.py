"""
byceps.services.shop.order.actions.award_badge
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from .....typing import UserID

from ....user_badge import awarding_service, badge_service
from ....user_badge.transfer.models import BadgeAwarding

from ...article.transfer.models import ArticleNumber

from .. import event_service
from ..dbmodels.order_action import Parameters
from ..transfer.models import Order, OrderID


def award_badge(
    order: Order,
    article_number: ArticleNumber,
    quantity: int,
    initiator_id: UserID,
    parameters: Parameters,
) -> None:
    """Award badge to user."""
    badge = badge_service.get_badge(parameters['badge_id'])
    user_id = order.placed_by_id

    for _ in range(quantity):
        awarding, _ = awarding_service.award_badge_to_user(badge.id, user_id)

        _create_order_event(order.id, awarding)


def _create_order_event(order_id: OrderID, awarding: BadgeAwarding) -> None:
    event_type = 'badge-awarded'
    data = {
        'awarding_id': str(awarding.id),
        'badge_id': str(awarding.badge_id),
        'recipient_id': str(awarding.user_id),
    }

    event_service.create_event(event_type, order_id, data)
