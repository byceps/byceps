"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import pytest

from byceps.services.shop.cart.models import Cart
from byceps.services.shop.order.models.orderer import Orderer
from byceps.services.shop.order import (
    sequence_service as order_sequence_service,
    service as order_service,
)
from byceps.services.shop.shop import service as shop_service
from byceps.services.shop.storefront import service as storefront_service
from byceps.services.site import service as site_service
from byceps.services.snippet import service as snippet_service

from testfixtures.shop_order import create_orderer

from tests.helpers import create_site, http_client, login_user
from tests.integration.services.shop.helpers import (
    create_shop,
    create_shop_fragment,
)


@pytest.fixture
def shop1(admin_app, email_config, admin_user):
    shop = create_shop('shop-1')
    snippet_id = create_payment_instructions_snippet(shop.id, admin_user.id)

    yield shop

    snippet_service.delete_snippet(snippet_id)
    shop_service.delete_shop(shop.id)


@pytest.fixture
def shop2(admin_app, email_config):
    shop = create_shop('shop-2')

    yield shop

    shop_service.delete_shop(shop.id)


@pytest.fixture
def order_number_sequence_id1(shop1) -> None:
    sequence_id = order_sequence_service.create_order_number_sequence(
        shop1.id, 'LF-02-B'
    )

    yield sequence_id

    order_sequence_service.delete_order_number_sequence(sequence_id)


@pytest.fixture
def order_number_sequence_id2(shop2) -> None:
    sequence_id = order_sequence_service.create_order_number_sequence(
        shop2.id, 'SHOP-02-B'
    )

    yield sequence_id

    order_sequence_service.delete_order_number_sequence(sequence_id)


@pytest.fixture
def storefront1(shop1, order_number_sequence_id1) -> None:
    storefront = storefront_service.create_storefront(
        f'{shop1.id}-storefront',
        shop1.id,
        order_number_sequence_id1,
        closed=False,
    )

    yield storefront

    storefront_service.delete_storefront(storefront.id)


@pytest.fixture
def storefront2(shop2, order_number_sequence_id2) -> None:
    storefront = storefront_service.create_storefront(
        f'{shop2.id}-storefront',
        shop2.id,
        order_number_sequence_id2,
        closed=False,
    )

    yield storefront

    storefront_service.delete_storefront(storefront.id)


@pytest.fixture
def site1(brand, storefront1):
    site = create_site('site1', brand.id, storefront_id=storefront1.id)
    yield site
    site_service.delete_site(site.id)


@pytest.fixture
def site2(brand, storefront2):
    site = create_site('site2', brand.id, storefront_id=storefront2.id)
    yield site
    site_service.delete_site(site.id)


@pytest.fixture
def site1_app(site1, make_site_app):
    app = make_site_app(SITE_ID=site1.id)
    with app.app_context():
        yield app


@pytest.fixture
def site2_app(site2, make_site_app):
    app = make_site_app(SITE_ID=site2.id)
    with app.app_context():
        yield app


@pytest.fixture(scope='module')
def user1(make_user_with_detail):
    return make_user_with_detail('OrdersUser1')


@pytest.fixture(scope='module')
def user2(make_user_with_detail):
    return make_user_with_detail('OrdersUser2')


@pytest.fixture
def order(storefront1, user1):
    orderer = create_orderer(user1)
    cart = Cart()

    order, _ = order_service.place_order(storefront1.id, orderer, cart)

    yield order

    order_service.delete_order(order.id)


def test_view_matching_user_and_site_and_shop(site1_app, order, user1):
    response = request_view(site1_app, user1, order.id)

    assert response.status_code == 200


def test_view_matching_site_and_shop_but_different_user(
    site1_app, order, user1, user2
):
    response = request_view(site1_app, user2, order.id)

    assert response.status_code == 404


def test_view_matching_user_but_different_site_and_shop(
    site2_app, order, user1
):
    response = request_view(site2_app, user1, order.id)

    assert response.status_code == 404


# helpers


def create_payment_instructions_snippet(shop_id, admin_id):
    return create_shop_fragment(
        shop_id, admin_id, 'payment_instructions', 'Send all ur moneyz!'
    )


def request_view(app, current_user, order_id):
    login_user(current_user.id)

    url = f'/shop/orders/{order_id!s}'

    with http_client(app, user_id=current_user.id) as client:
        response = client.get(url)

    return response
