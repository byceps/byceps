"""
byceps.services.party.transfer.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from ....typing import BrandID, PartyID

from ...shop.shop.transfer.models import ShopID


@dataclass(frozen=True)
class Party:
    id: PartyID
    brand_id: BrandID
    title: str
    starts_at: datetime
    ends_at: datetime
    max_ticket_quantity: Optional[int]
    shop_id: ShopID
    ticket_management_enabled: bool
    seat_management_enabled: bool
    archived: bool


@dataclass(frozen=True)
class PartySetting:
    party_id: PartyID
    name: str
    value: str
