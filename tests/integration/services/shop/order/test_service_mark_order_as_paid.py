"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import pytest

from byceps.services.shop.order import event_service, service as order_service
from byceps.services.shop.order.transfer.models import (
    PaymentMethod,
    PaymentState,
)
from byceps.util.iterables import find


@pytest.fixture
def order(admin_app, shop, order_number_sequence_id, orderer, empty_cart):
    order, _ = order_service.place_order(shop.id, orderer, empty_cart)
    yield order
    order_service.delete_order(order.id)


def test_mark_order_as_paid(order, admin_user):
    order_before = order
    assert order_before.payment_method is None
    assert order_before.payment_state == PaymentState.open
    assert order_before.is_open
    assert not order_before.is_paid

    order_service.mark_order_as_paid(
        order.id, PaymentMethod.cash, admin_user.id
    )

    order_after = order_service.find_order(order.id)
    assert order_after.payment_method == PaymentMethod.cash
    assert order_after.payment_state == PaymentState.paid
    assert not order_after.is_open
    assert order_after.is_paid


def test_additional_event_data(order, admin_user):
    additional_event_data = {
        # attempts to override internal properties
        'initiator_id': 'fake-initiator-id',
        'former_payment_state': 'random',
        'payment_method': 'telepathy',
        # custom properties
        'external_payment_id': '555-gimme-da-moneys',
    }

    paid_event = order_service.mark_order_as_paid(
        order.id,
        PaymentMethod.cash,
        admin_user.id,
        additional_event_data=additional_event_data,
    )

    events = event_service.get_events_for_order(order.id)
    paid_event = find(lambda e: e.event_type == 'order-paid', events)

    # Internal properties must not be overridden by additional event
    # data passed to the service.
    assert paid_event.data['initiator_id'] == str(admin_user.id)
    assert paid_event.data['former_payment_state'] == 'open'
    assert paid_event.data['payment_method'] == 'cash'

    # Other properties get passed unchanged.
    assert paid_event.data['external_payment_id'] == '555-gimme-da-moneys'
