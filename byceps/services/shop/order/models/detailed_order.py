"""
byceps.services.shop.order.models.detailed_order
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from typing import Optional

from ....user.models.user import User

from ...shop.models import ShopID
from ...storefront.models import StorefrontID

from .order import Address, BaseOrder, LineItem
from .payment import Payment


@dataclass(frozen=True)
class DetailedOrder(BaseOrder):
    shop_id: ShopID
    storefront_id: StorefrontID
    company: Optional[str]
    first_name: str
    last_name: str
    address: Address
    line_items: list[LineItem]
    payment_method: Optional[str]
    is_invoiced: bool
    is_processing_required: bool
    is_processed: bool
    cancelation_reason: Optional[str]


@dataclass(frozen=True)
class AdminDetailedOrder(DetailedOrder):
    placed_by: User
    payments: list[Payment]
