"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import pytest

from byceps.services.shop.cart.models import Cart
from byceps.services.shop.order.models.orderer import Orderer
from byceps.services.shop.order import service as order_service
from byceps.services.shop.sequence import service as sequence_service

from testfixtures.shop_order import create_orderer

from tests.helpers import (
    create_brand,
    create_party,
    create_site,
    create_user,
    create_user_with_detail,
    http_client,
    login_user,
)
from tests.services.shop.helpers import create_shop, create_shop_fragment


@pytest.fixture
def app(party_app_with_db):
    yield party_app_with_db


@pytest.fixture
def brand():
    return create_brand()


@pytest.fixture
def party1(brand, shop1):
    return create_party(brand.id, shop_id=shop1.id)


@pytest.fixture
def party2(brand, shop2):
    return create_party(
        brand.id, 'otherlan-2013', 'OtherLAN 2013', shop_id=shop2.id
    )


@pytest.fixture
def email_config(app, make_email_config):
    return make_email_config()


@pytest.fixture
def shop1(app, email_config, admin):
    shop = create_shop('shop-1')
    sequence_service.create_order_number_sequence(shop.id, 'LF-02-B')
    create_payment_instructions_snippet(shop.id, admin.id)
    return shop


@pytest.fixture
def shop2(app, email_config):
    return create_shop('shop-2')


@pytest.fixture
def admin(app):
    return create_user('ShopOrderAdmin')


@pytest.fixture
def user1(app):
    return create_user_with_detail('User1')


@pytest.fixture
def user2(app):
    return create_user_with_detail('User2')


def test_view_matching_user_and_party_and_shop(
    app, party1, shop1, admin, user1
):
    create_site(party_id=party1.id)

    order_id = place_order(shop1.id, user1)

    response = request_view(app, user1, order_id)

    assert response.status_code == 200


def test_view_matching_party_and_shop_but_different_user(
    app, party1, shop1, admin, user1, user2
):
    create_site(party_id=party1.id)

    order_id = place_order(shop1.id, user1)

    response = request_view(app, user2, order_id)

    assert response.status_code == 404


def test_view_matching_user_but_different_party_and_shop(
    app, party2, shop1, admin, user1
):
    create_site(party_id=party2.id)

    order_id = place_order(shop1.id, user1)

    response = request_view(app, user1, order_id)

    assert response.status_code == 404


# helpers


def create_payment_instructions_snippet(shop_id, admin_id):
    create_shop_fragment(
        shop_id, admin_id, 'payment_instructions', 'Send all ur moneyz!'
    )


def place_order(shop_id, user):
    orderer = create_orderer(user)
    cart = Cart()

    order, _ = order_service.place_order(shop_id, orderer, cart)

    return order.id


def request_view(app, current_user, order_id):
    login_user(current_user.id)

    url = f'/shop/orders/{order_id!s}'

    with http_client(app, user_id=current_user.id) as client:
        response = client.get(url)

    return response
