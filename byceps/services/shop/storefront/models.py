"""
byceps.services.shop.storefront.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2024 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from typing import NewType

from byceps.services.shop.catalog.models import CatalogID
from byceps.services.shop.order.models.number import OrderNumberSequenceID
from byceps.services.shop.shop.models import ShopID


StorefrontID = NewType('StorefrontID', str)


@dataclass(frozen=True)
class Storefront:
    id: StorefrontID
    shop_id: ShopID
    catalog_id: CatalogID | None
    order_number_sequence_id: OrderNumberSequenceID
    closed: bool


@dataclass(frozen=True)
class StorefrontForAdmin(Storefront):
    order_number_prefix: str
