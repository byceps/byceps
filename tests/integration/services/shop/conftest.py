"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from moneyed import EUR
import pytest

from byceps.services.brand.models import Brand
from byceps.services.shop.cart.models import Cart
from byceps.services.shop.shop.models import Shop
from byceps.services.shop.storefront.models import Storefront
from byceps.services.snippet.models import Scope
from byceps.services.snippet import snippet_service
from byceps.services.user.models.user import User


@pytest.fixture
def shop_brand(make_brand, make_email_config) -> Brand:
    brand = make_brand()
    make_email_config(brand.id, sender_address='noreply@acmecon.test')

    return brand


@pytest.fixture
def email_footer_snippets(shop_brand: Brand, admin_user: User) -> None:
    scope = Scope.for_brand(shop_brand.id)

    snippet_service.create_snippet(
        scope,
        'email_footer',
        'de',
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


@pytest.fixture
def shop(shop_brand: Brand, make_email_config, make_shop) -> Shop:
    return make_shop(shop_brand.id)


@pytest.fixture
def storefront(
    shop: Shop, make_order_number_sequence, make_storefront
) -> Storefront:
    order_number_sequence = make_order_number_sequence(shop.id)

    return make_storefront(shop.id, order_number_sequence.id)


@pytest.fixture
def empty_cart() -> Cart:
    return Cart(EUR)
