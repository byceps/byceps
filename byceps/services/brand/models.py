"""
byceps.services.brand.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from typing import NewType


BrandID = NewType('BrandID', str)


@dataclass(frozen=True, kw_only=True)
class Brand:
    id: BrandID
    title: str
    image_filename: str | None
    image_url_path: str | None
    archived: bool


@dataclass(frozen=True, kw_only=True)
class BrandSetting:
    brand_id: BrandID
    name: str
    value: str
