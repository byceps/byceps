"""
byceps.services.shop.shop.transfer.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import NewType

from attr import attrib, attrs

from .....typing import PartyID


ShopID = NewType('ShopID', str)


@attrs(frozen=True, slots=True)
class Shop:
    id = attrib(type=ShopID)
    party_id = attrib(type=PartyID)
