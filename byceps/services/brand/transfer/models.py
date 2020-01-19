"""
byceps.services.brand.transfer.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from dataclasses import dataclass

from ....typing import BrandID


@dataclass(frozen=True)
class Brand:
    id: BrandID
    title: str


@dataclass(frozen=True)
class BrandSetting:
    brand_id: BrandID
    name: str
    value: str
