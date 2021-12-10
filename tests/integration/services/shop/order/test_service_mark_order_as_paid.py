"""
:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.services.shop.order import log_service, service as order_service
from byceps.services.shop.order.transfer.models.order import PaymentState
from byceps.util.iterables import find

from tests.integration.services.shop.helpers import create_orderer


@pytest.fixture(scope='module')
def orderer(make_user):
    user = make_user()
    return create_orderer(user.id)


@pytest.fixture
def order(admin_app, storefront, orderer, empty_cart):
    order, _ = order_service.place_order(storefront.id, orderer, empty_cart)
    yield order
    order_service.delete_order(order.id)


def test_mark_order_as_paid(order, admin_user):
    order_before = order
    assert order_before.payment_method is None
    assert order_before.payment_state == PaymentState.open
    assert order_before.is_open
    assert not order_before.is_paid

    order_service.mark_order_as_paid(order.id, 'cash', admin_user.id)

    order_after = order_service.get_order(order.id)
    assert order_after.payment_method == 'cash'
    assert order_after.payment_state == PaymentState.paid
    assert not order_after.is_open
    assert order_after.is_paid


def test_additional_log_entry_data(order, admin_user):
    additional_log_entry_data = {
        # attempts to override internal properties
        'initiator_id': 'fake-initiator-id',
        'former_payment_state': 'random',
        'payment_method': 'telepathy',
        # custom properties
        'external_payment_id': '555-gimme-da-moneys',
    }

    order_service.mark_order_as_paid(
        order.id,
        'cash',
        admin_user.id,
        additional_log_entry_data=additional_log_entry_data,
    )

    log_entries = log_service.get_entries_for_order(order.id)
    paid_log_entry = find(log_entries, lambda e: e.event_type == 'order-paid')

    # Internal properties must not be overridden by additional log entry
    # data passed to the service.
    assert paid_log_entry.data['initiator_id'] == str(admin_user.id)
    assert paid_log_entry.data['former_payment_state'] == 'open'
    assert paid_log_entry.data['payment_method'] == 'cash'

    # Other properties get passed unchanged.
    assert paid_log_entry.data['external_payment_id'] == '555-gimme-da-moneys'
