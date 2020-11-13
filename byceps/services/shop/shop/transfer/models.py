"""
byceps.services.shop.shop.transfer.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from typing import Any, Dict, NewType


ShopID = NewType('ShopID', str)


@dataclass(frozen=True)
class Shop:
    id: ShopID
    title: str
    email_config_id: str
    archived: bool
    extra_settings: Dict[str, Any]
