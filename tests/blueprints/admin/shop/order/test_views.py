"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from unittest.mock import patch

import pytest

from byceps.events.shop import ShopOrderCanceled, ShopOrderPaid
from byceps.services.shop.article.models.article import Article
from byceps.services.shop.cart.models import Cart
from byceps.services.shop.order.models.order import Order
from byceps.services.shop.order import service as order_service
from byceps.services.shop.order.transfer.models import (
    PaymentMethod,
    PaymentState,
)
from byceps.services.shop.sequence import service as sequence_service

from testfixtures.shop_order import create_orderer

from tests.helpers import (
    assign_permissions_to_user,
    create_user,
    create_user_with_detail,
    http_client,
    login_user,
)
from tests.services.shop.helpers import create_article as _create_article


@pytest.fixture(scope='module')
def order_number_sequence(shop) -> None:
    sequence_service.create_order_number_sequence(shop.id, 'order-')


@pytest.fixture(scope='module')
def admin():
    admin = create_user('ShopOrderAdmin')
    authorize_admin(admin.id)
    login_user(admin.id)
    return admin


@pytest.fixture(scope='module')
def orderer():
    user = create_user_with_detail('Besteller')
    return create_orderer(user)


@patch('byceps.blueprints.shop.order.signals.order_canceled.send')
@patch('byceps.blueprints.admin.shop.order.views.order_email_service')
def test_cancel_before_paid(
    order_email_service_mock,
    order_canceled_signal_send_mock,
    app,
    shop,
    order_number_sequence,
    admin,
    orderer,
):
    article_before = create_article(shop.id, 'item-001', 8)

    quantified_articles_to_order = {(article_before, 3)}
    placed_order = place_order(shop.id, orderer, quantified_articles_to_order)
    order_before = get_order(placed_order.id)

    assert article_before.quantity == 5

    assert_payment_is_open(order_before)

    url = f'/admin/shop/orders/{order_before.id}/cancel'
    form_data = {
        'reason': 'Dein Vorname ist albern!',
        'send_email': 'y',
    }
    with http_client(app, user_id=admin.id) as client:
        response = client.post(url, data=form_data)

    order_afterwards = get_order(order_before.id)
    assert response.status_code == 302
    assert_payment(
        order_afterwards, None, PaymentState.canceled_before_paid, admin.id
    )

    article_afterwards = Article.query.get(article_before.id)
    assert article_afterwards.quantity == 8

    order_email_service_mock.send_email_for_canceled_order_to_orderer.assert_called_once_with(
        placed_order.id
    )

    event = ShopOrderCanceled(
        occurred_at=order_afterwards.payment_state_updated_at,
        order_id=placed_order.id,
        initiator_id=admin.id,
    )
    order_canceled_signal_send_mock.assert_called_once_with(None, event=event)


@patch('byceps.blueprints.shop.order.signals.order_canceled.send')
@patch('byceps.blueprints.admin.shop.order.views.order_email_service')
def test_cancel_before_paid_without_sending_email(
    order_email_service_mock,
    order_canceled_signal_send_mock,
    app,
    shop,
    order_number_sequence,
    admin,
    orderer,
):
    article_before = create_article(shop.id, 'item-002', 8)
    quantified_articles_to_order = {(article_before, 3)}
    placed_order = place_order(shop.id, orderer, quantified_articles_to_order)

    url = f'/admin/shop/orders/{placed_order.id}/cancel'
    form_data = {
        'reason': 'Dein Vorname ist albern!',
        # Sending e-mail is not requested.
    }
    with http_client(app, user_id=admin.id) as client:
        response = client.post(url, data=form_data)

    order_afterwards = get_order(placed_order.id)
    assert response.status_code == 302

    # No e-mail should be send.
    order_email_service_mock.send_email_for_canceled_order_to_orderer.assert_not_called()

    event = ShopOrderCanceled(
        occurred_at=order_afterwards.payment_state_updated_at,
        order_id=placed_order.id,
        initiator_id=admin.id,
    )
    order_canceled_signal_send_mock.assert_called_once_with(None, event=event)


@patch('byceps.blueprints.shop.order.signals.order_paid.send')
@patch('byceps.blueprints.admin.shop.order.views.order_email_service')
def test_mark_order_as_paid(
    order_email_service_mock,
    order_paid_signal_send_mock,
    app,
    shop,
    order_number_sequence,
    admin,
    orderer,
):
    placed_order = place_order(shop.id, orderer, [])
    order_before = get_order(placed_order.id)

    assert_payment_is_open(order_before)

    url = f'/admin/shop/orders/{order_before.id}/mark_as_paid'
    form_data = {'payment_method': 'direct_debit'}
    with http_client(app, user_id=admin.id) as client:
        response = client.post(url, data=form_data)

    order_afterwards = get_order(order_before.id)
    assert response.status_code == 302
    assert_payment(
        order_afterwards,
        PaymentMethod.direct_debit,
        PaymentState.paid,
        admin.id,
    )

    order_email_service_mock.send_email_for_paid_order_to_orderer.assert_called_once_with(
        placed_order.id
    )

    event = ShopOrderPaid(
        occurred_at=order_afterwards.payment_state_updated_at,
        order_id=placed_order.id,
        initiator_id=admin.id,
    )

    order_paid_signal_send_mock.assert_called_once_with(None, event=event)


@patch('byceps.blueprints.shop.order.signals.order_canceled.send')
@patch('byceps.blueprints.shop.order.signals.order_paid.send')
@patch('byceps.blueprints.admin.shop.order.views.order_email_service')
def test_cancel_after_paid(
    order_email_service_mock,
    order_paid_signal_send_mock,
    order_canceled_signal_send_mock,
    app,
    shop,
    order_number_sequence,
    admin,
    orderer,
):
    article_before = create_article(shop.id, 'item-003', 8)

    quantified_articles_to_order = {(article_before, 3)}
    placed_order = place_order(shop.id, orderer, quantified_articles_to_order)
    order_before = get_order(placed_order.id)

    assert article_before.quantity == 5

    assert_payment_is_open(order_before)

    url = f'/admin/shop/orders/{order_before.id}/mark_as_paid'
    form_data = {'payment_method': 'bank_transfer'}
    with http_client(app, user_id=admin.id) as client:
        response = client.post(url, data=form_data)

    url = f'/admin/shop/orders/{order_before.id}/cancel'
    form_data = {
        'reason': 'Dein Vorname ist albern!',
        'send_email': 'n',
    }
    with http_client(app, user_id=admin.id) as client:
        response = client.post(url, data=form_data)

    order_afterwards = get_order(order_before.id)
    assert response.status_code == 302
    assert_payment(
        order_afterwards,
        PaymentMethod.bank_transfer,
        PaymentState.canceled_after_paid,
        admin.id,
    )

    article_afterwards = Article.query.get(article_before.id)
    assert article_afterwards.quantity == 8

    order_email_service_mock.send_email_for_canceled_order_to_orderer.assert_called_once_with(
        placed_order.id
    )

    event = ShopOrderCanceled(
        occurred_at=order_afterwards.payment_state_updated_at,
        order_id=placed_order.id,
        initiator_id=admin.id,
    )
    order_canceled_signal_send_mock.assert_called_once_with(None, event=event)


# helpers


def authorize_admin(admin_id):
    permission_ids = {
        'admin.access',
        'shop_order.cancel',
        'shop_order.mark_as_paid',
    }
    assign_permissions_to_user(admin_id, 'admin', permission_ids)


def create_article(shop_id, item_number, quantity):
    return _create_article(
        shop_id,
        item_number=item_number,
        description=item_number,
        quantity=quantity,
    )


def place_order(shop_id, orderer, quantified_articles):
    cart = Cart()

    for article, quantity_to_order in quantified_articles:
        cart.add_item(article, quantity_to_order)

    order, _ = order_service.place_order(shop_id, orderer, cart)

    return order


def assert_payment_is_open(order):
    assert order.payment_method is None  # default
    assert order.payment_state == PaymentState.open
    assert order.payment_state_updated_at is None
    assert order.payment_state_updated_by_id is None


def assert_payment(order, method, state, updated_by_id):
    assert order.payment_method == method
    assert order.payment_state == state
    assert order.payment_state_updated_at is not None
    assert order.payment_state_updated_by_id == updated_by_id


def get_order(order_id):
    return Order.query.get(order_id)
