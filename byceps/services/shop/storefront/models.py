"""
byceps.services.shop.storefront.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from typing import NewType

from byceps.services.shop.catalog.models import Catalog
from byceps.services.shop.order.models.number import (
    OrderNumberSequence,
    OrderNumberSequenceID,
)
from byceps.services.shop.payment.models import PaymentGateway
from byceps.services.shop.shop.models import ShopID


StorefrontID = NewType('StorefrontID', str)


@dataclass(frozen=True, kw_only=True)
class Storefront:
    id: StorefrontID
    shop_id: ShopID
    catalog: Catalog | None
    order_number_sequence_id: OrderNumberSequenceID
    closed: bool


@dataclass(frozen=True, kw_only=True)
class StorefrontForAdmin(Storefront):
    order_number_sequence: OrderNumberSequence
    enabled_payment_gateways: set[PaymentGateway]
