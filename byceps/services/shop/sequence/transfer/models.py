"""
byceps.services.shop.sequence.transfer.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from enum import Enum

from attr import attrib, attrs

from ...shop.transfer.models import ShopID


Purpose = Enum('Purpose', ['article', 'order'])


@attrs(frozen=True, slots=True)
class NumberSequence:
    shop_id = attrib(type=ShopID)
    purpose = attrib(type=Purpose)
    prefix = attrib(type=str)
    value = attrib(type=int)
