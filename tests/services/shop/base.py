"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.services.shop.shop import service as shop_service

from tests.base import AbstractAppTestCase
from tests.helpers import DEFAULT_EMAIL_CONFIG_ID


class ShopTestBase(AbstractAppTestCase):

    # -------------------------------------------------------------------- #
    # helpers

    def create_shop(
        self, shop_id='shop-1', email_config_id=DEFAULT_EMAIL_CONFIG_ID
    ):
        return shop_service.create_shop(shop_id, shop_id, email_config_id)
