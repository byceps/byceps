"""
byceps.services.brand.transfer.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from attr import attrs

from ....typing import BrandID


@attrs(auto_attribs=True, frozen=True, slots=True)
class Brand:
    id: BrandID
    title: str


@attrs(auto_attribs=True, frozen=True, slots=True)
class BrandSetting:
    brand_id: BrandID
    name: str
    value: str
