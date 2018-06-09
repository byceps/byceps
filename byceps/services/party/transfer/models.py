"""
byceps.services.party.transfer.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from attr import attrib, attrs

from ....typing import PartyID


@attrs(frozen=True, slots=True)
class PartySetting:
    party_id = attrib(type=PartyID)
    name = attrib(type=str)
    value = attrib(type=str)
