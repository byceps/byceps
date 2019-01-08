"""
byceps.services.party.transfer.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime

from attr import attrib, attrs

from ....typing import BrandID, PartyID


@attrs(frozen=True, slots=True)
class Party:
    id = attrib(type=PartyID)
    brand_id = attrib(type=BrandID)
    title = attrib(type=str)
    starts_at = attrib(type=datetime)
    ends_at = attrib(type=datetime)
    archived = attrib(type=bool)


@attrs(frozen=True, slots=True)
class PartySetting:
    party_id = attrib(type=PartyID)
    name = attrib(type=str)
    value = attrib(type=str)
