"""
testfixtures.shop_shop
~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.services.shop.shop.models import Shop
from byceps.services.shop.shop.transfer.models import ShopID


def create_shop(shop_id: ShopID, email_config_id: str) -> Shop:
    party_id = shop_id
    title = shop_id

    return Shop(shop_id, title, party_id, email_config_id)
