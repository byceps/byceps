"""
byceps.services.shop.storefront.transfer.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from dataclasses import dataclass
from typing import NewType, Optional

from ...catalog.transfer.models import CatalogID
from ...order.transfer.models import OrderNumberSequenceID
from ...shop.transfer.models import ShopID


StorefrontID = NewType('StorefrontID', str)


@dataclass(frozen=True)
class Storefront:
    id: StorefrontID
    shop_id: ShopID
    catalog_id: Optional[CatalogID]
    order_number_sequence_id: OrderNumberSequenceID
    closed: bool
