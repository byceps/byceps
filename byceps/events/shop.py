"""
byceps.events.shop
~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from dataclasses import dataclass

from byceps.services.shop.order.models.number import OrderNumber
from byceps.services.shop.order.models.order import OrderID
from byceps.typing import UserID

from .base import _BaseEvent


@dataclass(frozen=True)
class _ShopOrderEvent(_BaseEvent):
    order_id: OrderID
    order_number: OrderNumber
    orderer_id: UserID
    orderer_screen_name: str | None


@dataclass(frozen=True)
class ShopOrderPlaced(_ShopOrderEvent):
    pass


@dataclass(frozen=True)
class ShopOrderCanceled(_ShopOrderEvent):
    pass


@dataclass(frozen=True)
class ShopOrderPaid(_ShopOrderEvent):
    payment_method: str
