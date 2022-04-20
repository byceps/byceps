"""
byceps.services.shop.order.transfer.invoice
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from .order import OrderID


@dataclass(frozen=True)
class Invoice:
    id: UUID
    order_id: OrderID
    number: str
    url: Optional[str]
