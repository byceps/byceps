"""
byceps.services.shop.shop.transfer.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from attr import attrib, attrs

from .....typing import PartyID

from ..models import ShopID


@attrs(frozen=True, slots=True)
class Shop:
    id = attrib(type=ShopID)
    party_id = attrib(type=PartyID)
