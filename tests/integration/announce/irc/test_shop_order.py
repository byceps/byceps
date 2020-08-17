"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import pytest

from byceps.announce.irc import shop_order  # Load signal handlers.
from byceps.events.shop import ShopOrderCanceled, ShopOrderPaid, ShopOrderPlaced
from byceps.services.shop.cart.models import Cart
from byceps.services.shop.order import service as order_service
from byceps.services.shop.order.transfer.models import PaymentMethod
from byceps.services.shop.sequence import service as sequence_service
from byceps.services.shop.shop import service as shop_service
from byceps.services.shop.storefront import service as storefront_service
from byceps.services.user import command_service as user_command_service
from byceps.signals import shop as shop_signals

from testfixtures.shop_order import create_orderer

from .helpers import (
    assert_submitted_data,
    CHANNEL_ORGA_LOG,
    CHANNEL_PUBLIC,
    mocked_irc_bot,
    now,
)


def test_shop_order_placed_announced(app, placed_order):
    expected_channels = [CHANNEL_ORGA_LOG]
    expected_text = 'Ken_von_Kaufkraft hat Bestellung ORDER-00001 aufgegeben.'

    order = placed_order
    event = ShopOrderPlaced(
        occurred_at=now(),
        order_id=order.id,
        order_number=order.order_number,
        orderer_id=order.placed_by_id,
        initiator_id=order.placed_by_id,
    )

    with mocked_irc_bot() as mock:
        shop_signals.order_placed.send(None, event=event)
        assert_submitted_data(mock, expected_channels, expected_text)


def test_shop_order_canceled_announced(app, canceled_order, shop_admin):
    expected_channels = [CHANNEL_ORGA_LOG]
    expected_text = (
        'ShoppingSheriff hat Bestellung ORDER-00002 von Ken_von_Kaufkraft '
        'storniert.'
    )

    order = canceled_order
    event = ShopOrderCanceled(
        occurred_at=now(),
        order_id=order.id,
        order_number=order.order_number,
        orderer_id=order.placed_by_id,
        initiator_id=shop_admin.id,
    )

    with mocked_irc_bot() as mock:
        shop_signals.order_canceled.send(None, event=event)
        assert_submitted_data(mock, expected_channels, expected_text)


def test_shop_order_paid_announced(app, paid_order, shop_admin):
    expected_channels = [CHANNEL_ORGA_LOG]
    expected_text = (
        'ShoppingSheriff hat Bestellung ORDER-00003 von Ken_von_Kaufkraft '
        'als per Überweisung bezahlt markiert.'
    )

    order = paid_order
    event = ShopOrderPaid(
        occurred_at=now(),
        order_id=order.id,
        order_number=order.order_number,
        orderer_id=order.placed_by_id,
        initiator_id=shop_admin.id,
    )

    with mocked_irc_bot() as mock:
        shop_signals.order_paid.send(None, event=event)
        assert_submitted_data(mock, expected_channels, expected_text)


# helpers


@pytest.fixture(scope='module')
def orderer(make_user_with_detail):
    user = make_user_with_detail('Ken_von_Kaufkraft')
    user_id = user.id
    yield create_orderer(user)
    user_command_service.delete_account(user_id, user_id, 'clean up')


@pytest.fixture(scope='module')
def shop_admin(make_user):
    return make_user('ShoppingSheriff')


@pytest.fixture(scope='module')
def shop(app, email_config):
    shop = shop_service.create_shop(
        'popup-store', 'Popup Store', email_config.id
    )

    yield shop

    shop_service.delete_shop(shop.id)


@pytest.fixture(scope='module')
def order_number_sequence_id(shop) -> None:
    sequence_id = sequence_service.create_order_number_sequence(
        shop.id, 'ORDER-'
    )

    yield sequence_id

    sequence_service.delete_order_number_sequence(sequence_id)


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
        placed_order.id, PaymentMethod.bank_transfer, shop_admin.id
    )

    return placed_order
