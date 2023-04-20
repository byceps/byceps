"""
byceps.services.brand.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from typing import Optional

from byceps.typing import BrandID


@dataclass(frozen=True)
class Brand:
    id: BrandID
    title: str
    image_filename: Optional[str]
    image_url_path: Optional[str]
    archived: bool


@dataclass(frozen=True)
class BrandSetting:
    brand_id: BrandID
    name: str
    value: str
