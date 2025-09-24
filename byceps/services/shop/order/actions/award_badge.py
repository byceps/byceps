"""
byceps.services.shop.order.actions.award_badge
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.services.shop.order import order_log_service
from byceps.services.shop.order.errors import OrderActionFailedError
from byceps.services.shop.order.models.action import ActionParameters
from byceps.services.shop.order.models.order import LineItem, Order, OrderID
from byceps.services.user.models.user import User
from byceps.services.user_badge import (
    user_badge_awarding_service,
    user_badge_service,
)
from byceps.services.user_badge.models import BadgeAwarding
from byceps.util.result import Ok, Result


def award_badge(
    order: Order,
    line_item: LineItem,
    initiator: User,
    parameters: ActionParameters,
) -> Result[None, OrderActionFailedError]:
    """Award badge to user."""
    badge = user_badge_service.get_badge(parameters['badge_id'])
    awardee = order.placed_by

    for _ in range(line_item.quantity):
        awarding, _ = user_badge_awarding_service.award_badge_to_user(
            badge, awardee
        )

        _create_order_log_entry(order.id, awarding)

    return Ok(None)


def _create_order_log_entry(order_id: OrderID, awarding: BadgeAwarding) -> None:
    event_type = 'badge-awarded'
    data = {
        'awarding_id': str(awarding.id),
        'badge_id': str(awarding.badge_id),
        'awardee_id': str(awarding.awardee_id),
    }

    order_log_service.create_db_entry(event_type, order_id, data)
