"""
byceps.services.brand.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import NewType, TYPE_CHECKING

if TYPE_CHECKING:
    from byceps.services.party.models import PartyID


BrandID = NewType('BrandID', str)


@dataclass(frozen=True)
class Brand:
    id: BrandID
    title: str
    image_filename: str | None
    image_url_path: str | None
    current_party_id: PartyID | None
    archived: bool


@dataclass(frozen=True)
class BrandSetting:
    brand_id: BrandID
    name: str
    value: str
