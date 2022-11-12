"""
:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.services.brand.transfer.models import Brand
from byceps.services.shop.article.transfer.models import Article
from byceps.services.shop.cart.models import Cart
from byceps.services.shop.order.transfer.order import Orderer
from byceps.services.shop.shop.transfer.models import Shop, ShopID
from byceps.services.shop.storefront.transfer.models import Storefront
from byceps.services.snippet import snippet_service
from byceps.services.snippet.transfer.models import Scope, SnippetID
from byceps.services.user.transfer.models import User
from byceps.typing import UserID

from tests.helpers.shop import create_article, create_orderer


@pytest.fixture
def shop_brand(make_brand, make_email_config) -> Brand:
    brand = make_brand()
    make_email_config(brand.id, sender_address='noreply@acmecon.test')

    return brand


@pytest.fixture
def email_footer_snippet_id(shop_brand: Brand, admin_user: User) -> SnippetID:
    scope = Scope.for_brand(shop_brand.id)

    version, _ = snippet_service.create_snippet(
        scope,
        'email_footer',
        admin_user.id,
        '''
Für Fragen stehen wir gerne zur Verfügung.

Viele Grüße,
das Team der Acme Entertainment Convention

-- 
Acme Entertainment Convention

E-Mail: noreply@acmecon.test
''',
    )

    return version.snippet_id


@pytest.fixture
def shop(shop_brand: Brand, make_email_config, make_shop) -> Shop:
    return make_shop(shop_brand.id)


@pytest.fixture
def storefront(
    shop: Shop, make_order_number_sequence, make_storefront
) -> Storefront:
    order_number_sequence = make_order_number_sequence(shop.id)

    return make_storefront(shop.id, order_number_sequence.id)


@pytest.fixture(scope='session')
def make_article():
    def _wrapper(shop_id: ShopID, **kwargs) -> Article:
        return create_article(shop_id, **kwargs)

    return _wrapper


@pytest.fixture(scope='session')
def make_orderer():
    def _wrapper(user_id: UserID) -> Orderer:
        return create_orderer(user_id)

    return _wrapper


@pytest.fixture
def empty_cart() -> Cart:
    return Cart()
