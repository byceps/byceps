"""
byceps.services.shop.order.models.invoice
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2024 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from uuid import UUID

from .order import OrderID


@dataclass(frozen=True)
class Invoice:
    id: UUID
    order_id: OrderID
    number: str
    url: str | None
