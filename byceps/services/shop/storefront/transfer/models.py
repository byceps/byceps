"""
byceps.services.shop.storefront.transfer.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from typing import NewType, Optional

from ...catalog.transfer.models import CatalogID
from ...order.transfer.models.number_sequence import OrderNumberSequenceID
from ...shop.transfer.models import ShopID


StorefrontID = NewType('StorefrontID', str)


@dataclass(frozen=True)
class Storefront:
    id: StorefrontID
    shop_id: ShopID
    catalog_id: Optional[CatalogID]
    order_number_sequence_id: OrderNumberSequenceID
    closed: bool
