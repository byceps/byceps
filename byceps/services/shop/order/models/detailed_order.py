"""
byceps.services.shop.order.models.detailed_order
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from dataclasses import dataclass

from byceps.services.shop.shop.models import ShopID
from byceps.services.shop.storefront.models import StorefrontID
from byceps.services.user.models.user import User

from .invoice import Invoice
from .order import Address, BaseOrder, LineItem
from .payment import Payment


@dataclass(frozen=True)
class DetailedOrder(BaseOrder):
    placed_by: User
    shop_id: ShopID
    storefront_id: StorefrontID
    company: str | None
    first_name: str
    last_name: str
    address: Address
    line_items: list[LineItem]
    payment_method: str | None
    is_invoiced: bool
    is_processing_required: bool
    is_processed: bool
    cancelation_reason: str | None


@dataclass(frozen=True)
class AdminDetailedOrder(DetailedOrder):
    invoices: list[Invoice]
    payments: list[Payment]
