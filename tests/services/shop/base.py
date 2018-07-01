"""
:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from testfixtures.shop_shop import create_shop

from tests.base import AbstractAppTestCase


class ShopTestBase(AbstractAppTestCase):

    # -------------------------------------------------------------------- #
    # helpers

    def create_shop(self, party_id):
        shop = create_shop(party_id)

        self.db.session.add(shop)
        self.db.session.commit()

        return shop
