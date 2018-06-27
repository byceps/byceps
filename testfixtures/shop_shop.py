"""
testfixtures.shop_shop
~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.services.shop.shop.models import Shop
from byceps.typing import PartyID


def create_shop(party_id: PartyID) -> Shop:
    shop_id = party_id

    return Shop(shop_id, party_id)
