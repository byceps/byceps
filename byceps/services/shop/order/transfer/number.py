"""
byceps.services.shop.order.transfer.number
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from typing import NewType
from uuid import UUID

from ...shop.transfer.models import ShopID


OrderNumberSequenceID = NewType('OrderNumberSequenceID', UUID)


@dataclass(frozen=True)
class OrderNumberSequence:
    id: OrderNumberSequenceID
    shop_id: ShopID
    prefix: str
    value: int


OrderNumber = NewType('OrderNumber', str)
