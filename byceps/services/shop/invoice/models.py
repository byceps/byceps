"""
byceps.services.shop.invoice.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from uuid import UUID

from byceps.services.shop.order.models.order import OrderID


@dataclass(frozen=True, kw_only=True)
class Invoice:
    id: UUID
    order_id: OrderID
    number: str
    url: str | None


@dataclass(frozen=True, kw_only=True)
class DownloadableInvoice:
    content_disposition: str
    content_type: str
    content: bytes
