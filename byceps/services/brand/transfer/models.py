"""
byceps.services.brand.transfer.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from attr import attrib, attrs

from ....typing import BrandID


@attrs(frozen=True, slots=True)
class BrandSetting:
    brand_id = attrib(type=BrandID)
    name = attrib(type=str)
    value = attrib(type=str)
