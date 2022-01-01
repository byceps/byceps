"""
byceps.services.party.transfer.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from ....typing import BrandID, PartyID

from ...brand.transfer.models import Brand


@dataclass(frozen=True)
class Party:
    id: PartyID
    brand_id: BrandID
    title: str
    starts_at: datetime
    ends_at: datetime
    max_ticket_quantity: Optional[int]
    ticket_management_enabled: bool
    seat_management_enabled: bool
    canceled: bool
    archived: bool

    @property
    def is_over(self) -> bool:
        """Returns true if the party has ended."""
        return self.ends_at < datetime.utcnow()


@dataclass(frozen=True)
class PartyWithBrand(Party):
    brand: Brand


@dataclass(frozen=True)
class PartySetting:
    party_id: PartyID
    name: str
    value: str
