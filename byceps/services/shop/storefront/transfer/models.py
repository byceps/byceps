"""
byceps.services.shop.storefront.transfer.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from dataclasses import dataclass
from typing import NewType

from ...sequence.transfer.models import NumberSequenceID
from ...shop.transfer.models import ShopID


StorefrontID = NewType('StorefrontID', str)


@dataclass(frozen=True)
class Storefront:
    id: StorefrontID
    shop_id: ShopID
    order_number_sequence_id: NumberSequenceID
    closed: bool
