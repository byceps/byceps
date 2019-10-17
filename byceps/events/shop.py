"""
byceps.events.shop
~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from dataclasses import dataclass

from ..services.shop.order.transfer.models import OrderID


@dataclass(frozen=True)
class _ShopOrderEvent:
    order_id: OrderID


@dataclass(frozen=True)
class ShopOrderPlaced(_ShopOrderEvent):
    pass


@dataclass(frozen=True)
class ShopOrderCanceled(_ShopOrderEvent):
    pass


@dataclass(frozen=True)
class ShopOrderPaid(_ShopOrderEvent):
    pass
