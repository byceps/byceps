"""
byceps.services.shop.shop.transfer.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Any, NewType

from .....typing import BrandID


ShopID = NewType('ShopID', str)


@dataclass(frozen=True)
class Shop:
    id: ShopID
    brand_id: BrandID
    title: str
    archived: bool
    extra_settings: dict[str, Any]
