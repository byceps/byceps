"""
byceps.services.shop.shop.transfer.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from dataclasses import dataclass
from typing import NewType


ShopID = NewType('ShopID', str)


@dataclass(frozen=True)
class Shop:
    id: ShopID
    title: str
    email_config_id: str
    closed: bool
    archived: bool
