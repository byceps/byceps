"""
byceps.services.shop.order.models.action
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any
from uuid import UUID

from byceps.services.shop.order.errors import OrderActionFailedError
from byceps.services.shop.product.models import ProductID
from byceps.services.user.models.user import User
from byceps.util.result import Result

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
    ]
    on_cancellation_after_payment: Callable[
        [Order, LineItem, User, ActionParameters],
        Result[None, OrderActionFailedError],
    ]
