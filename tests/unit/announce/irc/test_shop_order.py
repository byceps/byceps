"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from flask import Flask
import pytest

from byceps.announce.announce import build_announcement_request
from byceps.events.base import EventUser
from byceps.events.shop import (
    ShopOrderCanceledEvent,
    ShopOrderPaidEvent,
    ShopOrderPlacedEvent,
)
from byceps.services.shop.order.models.order import OrderID, OrderNumber

from tests.helpers import generate_uuid

from .helpers import assert_text


ORDER_ID = OrderID(generate_uuid())


def test_shop_order_placed_announced(
    app: Flask, now: datetime, orderer_user: EventUser, webhook_for_irc
):
    expected_text = 'Ken_von_Kaufkraft has placed order ORDER-00001.'

    event = ShopOrderPlacedEvent(
        occurred_at=now,
        initiator=orderer_user,
        order_id=ORDER_ID,
        order_number=OrderNumber('ORDER-00001'),
        orderer=orderer_user,
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


def test_shop_order_canceled_announced(
    app: Flask,
    now: datetime,
    shop_admin: EventUser,
    orderer_user: EventUser,
    webhook_for_irc,
):
    expected_text = (
        'ShoppingSheriff has canceled order ORDER-00002 by Ken_von_Kaufkraft.'
    )

    event = ShopOrderCanceledEvent(
        occurred_at=now,
        initiator=shop_admin,
        order_id=ORDER_ID,
        order_number=OrderNumber('ORDER-00002'),
        orderer=orderer_user,
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


def test_shop_order_paid_announced(
    app: Flask,
    now: datetime,
    shop_admin: EventUser,
    orderer_user: EventUser,
    webhook_for_irc,
):
    expected_text = (
        'ShoppingSheriff marked order ORDER-00003 by Ken_von_Kaufkraft '
        'as paid via bank transfer.'
    )

    event = ShopOrderPaidEvent(
        occurred_at=now,
        initiator=shop_admin,
        order_id=ORDER_ID,
        order_number=OrderNumber('ORDER-00003'),
        orderer=orderer_user,
        payment_method='bank_transfer',
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


# helpers


@pytest.fixture(scope='module')
def shop_admin(make_event_user) -> EventUser:
    return make_event_user(screen_name='ShoppingSheriff')


@pytest.fixture(scope='module')
def orderer_user(make_event_user) -> EventUser:
    return make_event_user(screen_name='Ken_von_Kaufkraft')
