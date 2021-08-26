"""
:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

import byceps.announce.connections  # Connect signal handlers.
from byceps.events.shop import ShopOrderCanceled, ShopOrderPaid, ShopOrderPlaced
from byceps.services.shop.cart.models import Cart
from byceps.services.shop.order import (
    sequence_service as order_sequence_service,
    service as order_service,
)
from byceps.services.shop.shop import service as shop_service
from byceps.services.shop.storefront import service as storefront_service
from byceps.signals import shop as shop_signals

from tests.integration.services.shop.helpers import create_orderer, create_shop

from .helpers import (
    assert_submitted_data,
    CHANNEL_ORGA_LOG,
    CHANNEL_PUBLIC,
    mocked_irc_bot,
    now,
)


def test_shop_order_placed_announced(app, placed_order, orderer_user):
    expected_channel = CHANNEL_ORGA_LOG
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
    expected_channel = CHANNEL_ORGA_LOG
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
    expected_channel = CHANNEL_ORGA_LOG
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
def orderer_user(make_user_with_detail):
    return make_user_with_detail('Ken_von_Kaufkraft')


@pytest.fixture(scope='module')
def orderer(orderer_user):
    yield create_orderer(orderer_user)


@pytest.fixture(scope='module')
def shop_admin(make_user):
    return make_user('ShoppingSheriff')


@pytest.fixture(scope='module')
def shop(app, make_brand):
    brand = make_brand()
    shop = create_shop(brand.id)

    yield shop

    shop_service.delete_shop(shop.id)


@pytest.fixture(scope='module')
def order_number_sequence_id(shop) -> None:
    sequence_id = order_sequence_service.create_order_number_sequence(
        shop.id, 'ORDER-'
    )

    yield sequence_id

    order_sequence_service.delete_order_number_sequence(sequence_id)


@pytest.fixture(scope='module')
def storefront(shop, order_number_sequence_id) -> None:
    storefront = storefront_service.create_storefront(
        f'{shop.id}-storefront', shop.id, order_number_sequence_id, closed=False
    )

    yield storefront

    storefront_service.delete_storefront(storefront.id)


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
