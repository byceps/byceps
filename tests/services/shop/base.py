"""
:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from testfixtures.shop_article import create_article
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

    def create_article(self, shop_id, *, quantity=1):
        article = create_article(shop_id, quantity=quantity)

        self.db.session.add(article)
        self.db.session.commit()

        return article
