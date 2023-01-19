"""
byceps.services.shop.order.models.number
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from typing import NewType
from uuid import UUID

from ...shop.models import ShopID


OrderNumberSequenceID = NewType('OrderNumberSequenceID', UUID)


@dataclass(frozen=True)
class OrderNumberSequence:
    id: OrderNumberSequenceID
    shop_id: ShopID
    prefix: str
    value: int


OrderNumber = NewType('OrderNumber', str)
