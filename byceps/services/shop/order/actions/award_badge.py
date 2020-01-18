"""
byceps.services.shop.order.actions.award_badge
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from .....typing import UserID

from ....user_badge import (
    command_service as badge_command_service,
    service as badge_service,
)
from ....user_badge.transfer.models import BadgeAwarding, BadgeID

from ...article.transfer.models import ArticleNumber

from .. import event_service
from ..models.order_action import Parameters
from ..transfer.models import Order, OrderID


def award_badge(
    order: Order,
    article_number: ArticleNumber,
    quantity: int,
    initiator_id: UserID,
    parameters: Parameters,
) -> None:
    """Award badge to user."""
    badge_id = parameters['badge_id']
    user_id = order.placed_by_id

    _verify_badge_id(badge_id)

    for _ in range(quantity):
        awarding, _ = badge_command_service.award_badge_to_user(
            badge_id, user_id
        )

        _create_order_event(order.id, awarding)


def _verify_badge_id(badge_id: BadgeID) -> None:
    """Raise exception if no badge with that ID is known."""
    badge = badge_service.find_badge(badge_id)

    if badge is None:
        raise ValueError(f'Unknown badge ID "{badge_id}"')


def _create_order_event(order_id: OrderID, awarding: BadgeAwarding) -> None:
    event_type = 'badge-awarded'
    data = {
        'awarding_id': str(awarding.id),
        'badge_id': str(awarding.badge_id),
        'recipient_id': str(awarding.user_id),
    }

    event_service.create_event(event_type, order_id, data)
