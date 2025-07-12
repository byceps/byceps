"""
byceps.services.shop.order.models.detailed_order
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass

from byceps.services.shop.invoice.models import Invoice
from byceps.services.shop.shop.models import ShopID
from byceps.services.shop.storefront.models import StorefrontID

from .order import Address, BaseOrder, LineItem
from .payment import Payment


@dataclass(frozen=True, kw_only=True)
class DetailedOrder(BaseOrder):
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
    cancellation_reason: str | None


@dataclass(frozen=True, kw_only=True)
class AdminDetailedOrder(DetailedOrder):
    invoices: list[Invoice]
    payments: list[Payment]
