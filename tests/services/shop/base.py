"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.services.snippet import service as snippet_service
from byceps.services.snippet.transfer.models import Scope

from testfixtures.shop_article import create_article
from testfixtures.shop_shop import create_shop

from tests.base import AbstractAppTestCase
from tests.helpers import create_user, DEFAULT_EMAIL_CONFIG_ID


class ShopTestBase(AbstractAppTestCase):

    # -------------------------------------------------------------------- #
    # helpers

    def create_shop(
        self, shop_id='shop-1', email_config_id=DEFAULT_EMAIL_CONFIG_ID
    ):
        shop = create_shop(shop_id, email_config_id)

        self.db.session.add(shop)
        self.db.session.commit()

        return shop

    def create_shop_fragment(self, shop_id, name, body):
        scope = Scope('shop', shop_id)

        try:
            self.admin
        except AttributeError:
            self.admin = create_user('Admin')

        snippet_service.create_fragment(scope, name, self.admin.id, body)

    def create_article(self, shop_id, **kwargs):
        article = create_article(shop_id, **kwargs)

        self.db.session.add(article)
        self.db.session.commit()

        return article
