"""
byceps.services.shop.sequence.transfer.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from dataclasses import dataclass
from enum import Enum
from typing import NewType
from uuid import UUID

from ...shop.transfer.models import ShopID


NumberSequenceID = NewType('NumberSequenceID', UUID)


Purpose = Enum('Purpose', ['article', 'order'])


@dataclass(frozen=True)
class NumberSequence:
    id: NumberSequenceID
    shop_id: ShopID
    purpose: Purpose
    prefix: str
    value: int
