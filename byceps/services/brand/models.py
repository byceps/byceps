"""
byceps.services.brand.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from dataclasses import dataclass

from byceps.typing import BrandID


@dataclass(frozen=True)
class Brand:
    id: BrandID
    title: str
    image_filename: str | None
    image_url_path: str | None
    archived: bool


@dataclass(frozen=True)
class BrandSetting:
    brand_id: BrandID
    name: str
    value: str
