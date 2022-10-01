"""
:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

import byceps.announce.connections  # Connect signal handlers.
from byceps.events.shop import ShopOrderCanceled, ShopOrderPaid, ShopOrderPlaced
from byceps.services.shop.cart.models import Cart
from byceps.services.shop.order import service as order_service
from byceps.services.shop.storefront.transfer.models import Storefront
from byceps.signals import shop as shop_signals

from tests.integration.services.shop.conftest import make_orderer

from .helpers import (
    assert_submitted_data,
    CHANNEL_INTERNAL,
    mocked_irc_bot,
    now,
)


def test_shop_order_placed_announced(app, placed_order, orderer_user):
    expected_channel = CHANNEL_INTERNAL
    expected_text = 'Ken_von_Kaufkraft hat Bestellung ORDER-00001 aufgegeben.'

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

    with mocked_irc_bot() as mock:
        shop_signals.order_placed.send(None, event=event)

    assert_submitted_data(mock, expected_channel, expected_text)


def test_shop_order_canceled_announced(
    app, canceled_order, orderer_user, shop_admin
):
    expected_channel = CHANNEL_INTERNAL
    expected_text = (
        'ShoppingSheriff hat Bestellung ORDER-00002 von Ken_von_Kaufkraft '
        'storniert.'
    )

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

    with mocked_irc_bot() as mock:
        shop_signals.order_canceled.send(None, event=event)

    assert_submitted_data(mock, expected_channel, expected_text)


def test_shop_order_paid_announced(app, paid_order, orderer_user, shop_admin):
    expected_channel = CHANNEL_INTERNAL
    expected_text = (
        'ShoppingSheriff hat Bestellung ORDER-00003 von Ken_von_Kaufkraft '
        'als per Überweisung bezahlt markiert.'
    )

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

    with mocked_irc_bot() as mock:
        shop_signals.order_paid.send(None, event=event)

    assert_submitted_data(mock, expected_channel, expected_text)


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
def shop(app, make_brand, make_shop):
    brand = make_brand()

    return make_shop(brand.id)


@pytest.fixture(scope='module')
def storefront(shop, make_order_number_sequence, make_storefront) -> Storefront:
    order_number_sequence = make_order_number_sequence(shop.id, prefix='ORDER-')

    return make_storefront(shop.id, order_number_sequence.id)


@pytest.fixture
def placed_order(storefront, orderer):
    order, _ = order_service.place_order(storefront.id, orderer, Cart())

    yield order

    order_service.delete_order(order.id)


@pytest.fixture
def canceled_order(placed_order, shop_admin):
    order_service.cancel_order(placed_order.id, shop_admin.id, 'Kein Geld!')

    return placed_order


@pytest.fixture
def paid_order(placed_order, shop_admin):
    order_service.mark_order_as_paid(
        placed_order.id, 'bank_transfer', shop_admin.id
    )

    return placed_order
