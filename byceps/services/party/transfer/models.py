"""
byceps.services.party.transfer.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime

from attr import attrs

from ....typing import BrandID, PartyID


@attrs(auto_attribs=True, frozen=True, slots=True)
class Party:
    id: PartyID
    brand_id: BrandID
    title: str
    starts_at: datetime
    ends_at: datetime
    max_ticket_quantity: int
    archived: bool


@attrs(auto_attribs=True, frozen=True, slots=True)
class PartySetting:
    party_id: PartyID
    name: str
    value: str
