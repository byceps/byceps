"""
byceps.services.shop.shop.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from typing import Any, NewType

from moneyed import Currency

from byceps.services.brand.models import BrandID


ShopID = NewType('ShopID', str)


@dataclass(frozen=True, kw_only=True)
class Shop:
    id: ShopID
    brand_id: BrandID
    title: str
    currency: Currency
    archived: bool
    extra_settings: dict[str, Any]
