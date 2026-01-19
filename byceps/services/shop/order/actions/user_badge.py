"""
byceps.services.shop.order.actions.award_badge
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.services.shop.order.errors import OrderActionFailedError
from byceps.services.shop.order.log import (
    order_log_domain_service,
    order_log_service,
)
from byceps.services.shop.order.models.action import (
    ActionParameters,
    ActionProcedure,
)
from byceps.services.shop.order.models.order import (
    LineItem,
    Order,
    OrderID,
    PaidOrder,
)
from byceps.services.user.models.user import User
from byceps.services.user_badge import (
    user_badge_awarding_service,
    user_badge_service,
)
from byceps.services.user_badge.models import BadgeAwarding
from byceps.util.result import Err, Ok, Result


def get_action_procedure() -> ActionProcedure:
    return ActionProcedure(
        on_payment=on_payment,
        on_cancellation_before_payment=on_cancellation_before_payment,
        on_cancellation_after_payment=on_cancellation_after_payment,
    )


def on_payment(
    order: PaidOrder,
    line_item: LineItem,
    initiator: User,
    parameters: ActionParameters,
) -> Result[None, OrderActionFailedError]:
    """Award badge to user."""
    badge = user_badge_service.get_badge(parameters['badge_id'])
    awardee = order.placed_by

    for _ in range(line_item.quantity):
        match user_badge_awarding_service.award_badge_to_user(badge, awardee):
            case Ok((awarding, _)):
                _create_order_log_entry(order.id, awarding)
            case Err(e):
                return Err(OrderActionFailedError(details=e))

    return Ok(None)


def _create_order_log_entry(order_id: OrderID, awarding: BadgeAwarding) -> None:
    log_entry = order_log_domain_service.build_user_badge_awarded_entry(
        order_id, awarding
    )

    order_log_service.persist_entry(log_entry)


def on_cancellation_before_payment(
    order: Order,
    line_item: LineItem,
    initiator: User,
    parameters: ActionParameters,
) -> Result[None, OrderActionFailedError]:
    return Ok(None)


def on_cancellation_after_payment(
    order: Order,
    line_item: LineItem,
    initiator: User,
    parameters: ActionParameters,
) -> Result[None, OrderActionFailedError]:
    return Ok(None)
