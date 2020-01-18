"""
byceps.services.shop.sequence.transfer.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from enum import Enum

from attr import attrs

from ...shop.transfer.models import ShopID


Purpose = Enum('Purpose', ['article', 'order'])


@attrs(auto_attribs=True, frozen=True, slots=True)
class NumberSequence:
    shop_id: ShopID
    purpose: Purpose
    prefix: str
    value: int
