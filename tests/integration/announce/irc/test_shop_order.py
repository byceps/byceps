"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from moneyed import EUR
import pytest

from byceps.announce.connections import build_announcement_request
from byceps.events.shop import ShopOrderCanceled, ShopOrderPaid, ShopOrderPlaced
from byceps.services.shop.cart.models import Cart
from byceps.services.shop.order import order_checkout_service, order_service
from byceps.services.shop.storefront.models import Storefront

from .helpers import build_announcement_request_for_irc, now


def test_shop_order_placed_announced(
    admin_app, placed_order, orderer_user, webhook_for_irc
):
    expected_text = 'Ken_von_Kaufkraft hat Bestellung ORDER-00001 aufgegeben.'
    expected = build_announcement_request_for_irc(expected_text)

    order = placed_order
    event = ShopOrderPlaced(
        occurred_at=now(),
        initiator_id=orderer_user.id,
        initiator_screen_name=orderer_user.screen_name,
        order_id=order.id,
        order_number=order.order_number,
        orderer_id=orderer_user.id,
        orderer_screen_name=orderer_user.screen_name,
    )

    assert build_announcement_request(event, webhook_for_irc) == expected


def test_shop_order_canceled_announced(
    admin_app, canceled_order, orderer_user, shop_admin, webhook_for_irc
):
    expected_text = (
        'ShoppingSheriff hat Bestellung ORDER-00002 von Ken_von_Kaufkraft '
        'storniert.'
    )
    expected = build_announcement_request_for_irc(expected_text)

    order = canceled_order
    event = ShopOrderCanceled(
        occurred_at=now(),
        initiator_id=shop_admin.id,
        initiator_screen_name=shop_admin.screen_name,
        order_id=order.id,
        order_number=order.order_number,
        orderer_id=orderer_user.id,
        orderer_screen_name=orderer_user.screen_name,
    )

    assert build_announcement_request(event, webhook_for_irc) == expected


def test_shop_order_paid_announced(
    admin_app, paid_order, orderer_user, shop_admin, webhook_for_irc
):
    expected_text = (
        'ShoppingSheriff hat Bestellung ORDER-00003 von Ken_von_Kaufkraft '
        'als per Überweisung bezahlt markiert.'
    )
    expected = build_announcement_request_for_irc(expected_text)

    order = paid_order
    event = ShopOrderPaid(
        occurred_at=now(),
        initiator_id=shop_admin.id,
        initiator_screen_name=shop_admin.screen_name,
        order_id=order.id,
        order_number=order.order_number,
        orderer_id=orderer_user.id,
        orderer_screen_name=orderer_user.screen_name,
        payment_method='bank_transfer',
    )

    assert build_announcement_request(event, webhook_for_irc) == expected


# helpers


@pytest.fixture(scope='module')
def orderer_user(make_user):
    return make_user('Ken_von_Kaufkraft')


@pytest.fixture(scope='module')
def orderer(make_orderer, orderer_user):
    return make_orderer(orderer_user.id)


@pytest.fixture(scope='module')
def shop_admin(make_user):
    return make_user('ShoppingSheriff')


@pytest.fixture(scope='module')
def shop(admin_app, make_brand, make_shop):
    brand = make_brand()

    return make_shop(brand.id)


@pytest.fixture(scope='module')
def storefront(shop, make_order_number_sequence, make_storefront) -> Storefront:
    order_number_sequence = make_order_number_sequence(shop.id, prefix='ORDER-')

    return make_storefront(shop.id, order_number_sequence.id)


@pytest.fixture
def placed_order(storefront, orderer):
    cart = Cart(EUR)
    order, _ = order_checkout_service.place_order(
        storefront.id, orderer, cart
    ).unwrap()

    return order


@pytest.fixture
def canceled_order(placed_order, shop_admin):
    order_service.cancel_order(
        placed_order.id, shop_admin.id, 'Kein Geld!'
    ).unwrap()

    return placed_order


@pytest.fixture
def paid_order(placed_order, shop_admin):
    order_service.mark_order_as_paid(
        placed_order.id, 'bank_transfer', shop_admin.id
    )

    return placed_order
