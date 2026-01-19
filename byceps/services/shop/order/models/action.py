"""
byceps.services.shop.order.models.action
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any
from uuid import UUID

from byceps.services.shop.order.errors import OrderActionFailedError
from byceps.services.shop.product.models import ProductID
from byceps.services.user.models.user import User
from byceps.util.result import Ok, Result

from .order import LineItem, Order, PaidOrder


ActionParameters = dict[str, Any]


@dataclass(frozen=True, kw_only=True)
class Action:
    id: UUID
    product_id: ProductID
    procedure_name: str
    parameters: ActionParameters


@dataclass(frozen=True, kw_only=True)
class ActionProcedure:
    on_payment: Callable[
        [PaidOrder, LineItem, User, ActionParameters],
        Result[None, OrderActionFailedError],
    ] = field(default_factory=lambda: on_payment_default)
    on_cancellation_before_payment: Callable[
        [Order, LineItem, User, ActionParameters],
        Result[None, OrderActionFailedError],
    ] = field(default_factory=lambda: on_cancellation_before_payment_default)
    on_cancellation_after_payment: Callable[
        [Order, LineItem, User, ActionParameters],
        Result[None, OrderActionFailedError],
    ] = field(default_factory=lambda: on_cancellation_after_payment_default)


def on_payment_default(
    order: PaidOrder,
    line_item: LineItem,
    initiator: User,
    parameters: ActionParameters,
) -> Result[None, OrderActionFailedError]:
    return Ok(None)


def on_cancellation_before_payment_default(
    order: Order,
    line_item: LineItem,
    initiator: User,
    parameters: ActionParameters,
) -> Result[None, OrderActionFailedError]:
    return Ok(None)


def on_cancellation_after_payment_default(
    order: Order,
    line_item: LineItem,
    initiator: User,
    parameters: ActionParameters,
) -> Result[None, OrderActionFailedError]:
    return Ok(None)
