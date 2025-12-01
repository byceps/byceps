"""
byceps.services.shop.order.events
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass

from byceps.services.core.events import BaseEvent
from byceps.services.shop.order.models.number import OrderNumber
from byceps.services.shop.order.models.order import OrderID
from byceps.services.user.models.user import User


@dataclass(frozen=True, kw_only=True)
class _ShopOrderEvent(BaseEvent):
    order_id: OrderID
    order_number: OrderNumber
    orderer: User


@dataclass(frozen=True, kw_only=True)
class ShopOrderPlacedEvent(_ShopOrderEvent):
    pass


@dataclass(frozen=True, kw_only=True)
class ShopOrderCanceledEvent(_ShopOrderEvent):
    pass


@dataclass(frozen=True, kw_only=True)
class ShopOrderPaidEvent(_ShopOrderEvent):
    payment_method: str
