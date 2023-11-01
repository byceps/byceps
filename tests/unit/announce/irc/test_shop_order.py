"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import Flask

from byceps.announce.announce import build_announcement_request
from byceps.events.shop import (
    ShopOrderCanceledEvent,
    ShopOrderPaidEvent,
    ShopOrderPlacedEvent,
)
from byceps.services.shop.order.models.order import OrderID, OrderNumber
from byceps.services.user.models.user import UserID

from tests.helpers import generate_uuid

from .helpers import assert_text, now


OCCURRED_AT = now()
SHOP_ADMIN_ID = UserID(generate_uuid())
ORDER_ID = OrderID(generate_uuid())
ORDERER_ID = UserID(generate_uuid())


def test_shop_order_placed_announced(app: Flask, webhook_for_irc):
    expected_text = 'Ken_von_Kaufkraft has placed order ORDER-00001.'

    event = ShopOrderPlacedEvent(
        occurred_at=OCCURRED_AT,
        initiator_id=ORDERER_ID,
        initiator_screen_name='Ken_von_Kaufkraft',
        order_id=ORDER_ID,
        order_number=OrderNumber('ORDER-00001'),
        orderer_id=ORDERER_ID,
        orderer_screen_name='Ken_von_Kaufkraft',
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


def test_shop_order_canceled_announced(app: Flask, webhook_for_irc):
    expected_text = (
        'ShoppingSheriff has canceled order ORDER-00002 by Ken_von_Kaufkraft.'
    )

    event = ShopOrderCanceledEvent(
        occurred_at=now(),
        initiator_id=SHOP_ADMIN_ID,
        initiator_screen_name='ShoppingSheriff',
        order_id=ORDER_ID,
        order_number=OrderNumber('ORDER-00002'),
        orderer_id=ORDERER_ID,
        orderer_screen_name='Ken_von_Kaufkraft',
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


def test_shop_order_paid_announced(app: Flask, webhook_for_irc):
    expected_text = (
        'ShoppingSheriff marked order ORDER-00003 by Ken_von_Kaufkraft '
        'as paid via bank transfer.'
    )

    event = ShopOrderPaidEvent(
        occurred_at=now(),
        initiator_id=SHOP_ADMIN_ID,
        initiator_screen_name='ShoppingSheriff',
        order_id=ORDER_ID,
        order_number=OrderNumber('ORDER-00003'),
        orderer_id=ORDERER_ID,
        orderer_screen_name='Ken_von_Kaufkraft',
        payment_method='bank_transfer',
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)
