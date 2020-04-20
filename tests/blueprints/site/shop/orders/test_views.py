"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import pytest

from byceps.services.brand import service as brand_service
from byceps.services.party import service as party_service
from byceps.services.shop.cart.models import Cart
from byceps.services.shop.order.models.orderer import Orderer
from byceps.services.shop.order import service as order_service
from byceps.services.shop.sequence import service as sequence_service
from byceps.services.shop.shop import service as shop_service
from byceps.services.site import service as site_service
from byceps.services.user import command_service as user_command_service

from testfixtures.shop_order import create_orderer

from tests.helpers import (
    create_brand,
    create_party,
    create_site,
    create_user_with_detail,
    http_client,
    login_user,
)
from tests.services.shop.helpers import create_shop, create_shop_fragment


@pytest.fixture
def app(party_app_with_db):
    yield party_app_with_db


@pytest.fixture
def brand(app):
    brand = create_brand()
    yield brand
    brand_service.delete_brand(brand.id)


@pytest.fixture
def party1(brand, shop1):
    party = create_party(brand.id, shop_id=shop1.id)
    yield party
    party_service.delete_party(party.id)


@pytest.fixture
def party2(brand, shop2):
    party = create_party(
        brand.id, 'otherlan-2013', 'OtherLAN 2013', shop_id=shop2.id
    )
    yield party
    party_service.delete_party(party.id)


@pytest.fixture
def site1(party1):
    site = create_site(party_id=party1.id)
    yield site
    site_service.delete_site(site.id)


@pytest.fixture
def site2(party2):
    site = create_site(party_id=party2.id)
    yield site
    site_service.delete_site(site.id)


@pytest.fixture
def shop1(app, email_config, admin_user):
    shop = create_shop('shop-1')
    sequence_service.create_order_number_sequence(shop.id, 'LF-02-B')
    create_payment_instructions_snippet(shop.id, admin_user.id)

    yield shop

    sequence_service.delete_order_number_sequence(shop.id)
    shop_service.delete_shop(shop.id)


@pytest.fixture
def shop2(app, email_config):
    shop = create_shop('shop-2')
    yield shop
    shop_service.delete_shop(shop.id)


@pytest.fixture
def user1(app):
    user = create_user_with_detail('User1')
    yield user
    user_command_service.delete_account(user.id, user.id, 'clean up')


@pytest.fixture
def user2(app):
    user = create_user_with_detail('User2')
    yield user
    user_command_service.delete_account(user.id, user.id, 'clean up')


@pytest.fixture
def order(shop1, user1):
    orderer = create_orderer(user1)
    cart = Cart()

    order, _ = order_service.place_order(shop1.id, orderer, cart)

    yield order

    order_service.delete_order(order.id)


def test_view_matching_user_and_party_and_shop(app, site1, order, user1):
    response = request_view(app, user1, order.id)

    assert response.status_code == 200


def test_view_matching_party_and_shop_but_different_user(
    app, site1, order, user1, user2
):
    response = request_view(app, user2, order.id)

    assert response.status_code == 404


def test_view_matching_user_but_different_party_and_shop(
    app, site2, order, user1
):
    response = request_view(app, user1, order.id)

    assert response.status_code == 404


# helpers


def create_payment_instructions_snippet(shop_id, admin_id):
    create_shop_fragment(
        shop_id, admin_id, 'payment_instructions', 'Send all ur moneyz!'
    )


def request_view(app, current_user, order_id):
    login_user(current_user.id)

    url = f'/shop/orders/{order_id!s}'

    with http_client(app, user_id=current_user.id) as client:
        response = client.get(url)

    return response
