"""
byceps.services.shop.order.models.invoice
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from .order import OrderID


@dataclass(frozen=True)
class Invoice:
    id: UUID
    order_id: OrderID
    number: str
    url: str | None
