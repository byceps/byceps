"""
byceps.events.shop
~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from typing import Optional

from ..services.shop.order.transfer.number import OrderNumber
from ..services.shop.order.transfer.order import OrderID
from ..typing import UserID

from .base import _BaseEvent


@dataclass(frozen=True)
class _ShopOrderEvent(_BaseEvent):
    order_id: OrderID
    order_number: OrderNumber
    orderer_id: UserID
    orderer_screen_name: Optional[str]


@dataclass(frozen=True)
class ShopOrderPlaced(_ShopOrderEvent):
    pass


@dataclass(frozen=True)
class ShopOrderCanceled(_ShopOrderEvent):
    pass


@dataclass(frozen=True)
class ShopOrderPaid(_ShopOrderEvent):
    payment_method: str
