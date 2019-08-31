"""
byceps.services.shop.shop.transfer.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import NewType

from attr import attrs

from .....typing import PartyID


ShopID = NewType('ShopID', str)


@attrs(auto_attribs=True, frozen=True, slots=True)
class Shop:
    id: ShopID
    party_id: PartyID
    email_config_id: str
    closed: bool
    archived: bool
