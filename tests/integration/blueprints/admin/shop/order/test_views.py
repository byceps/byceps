"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from unittest.mock import patch

import pytest

from byceps.events.shop import ShopOrderCanceled, ShopOrderPaid
from byceps.services.authorization import service as authorization_service
from byceps.services.shop.article import service as article_service
from byceps.services.shop.cart.models import Cart
from byceps.services.shop.order.models.order import Order
from byceps.services.shop.order import service as order_service
from byceps.services.shop.order.transfer.models import (
    PaymentMethod,
    PaymentState,
)
from testfixtures.shop_order import create_orderer

from tests.helpers import (
    create_permissions,
    create_role_with_permissions_assigned,
    http_client,
    login_user,
)
from tests.integration.services.shop.helpers import (
    create_article as _create_article,
)


@pytest.fixture(scope='module')
def admin(make_user):
    admin = make_user('ShopOrderAdmin')

    permission_ids = {
        'admin.access',
        'shop_order.cancel',
        'shop_order.mark_as_paid',
    }
    role_id = 'order_admin'
    create_permissions(permission_ids)
    create_role_with_permissions_assigned(role_id, permission_ids)
    authorization_service.assign_role_to_user(role_id, admin.id)

    login_user(admin.id)

    yield admin

    authorization_service.deassign_all_roles_from_user(admin.id, admin.id)
    authorization_service.delete_role(role_id)
    for permission_id in permission_ids:
        authorization_service.delete_permission(permission_id)


@pytest.fixture
def article1(shop):
    article = create_article(shop.id, 'item-001', 8)
    article_id = article.id
    yield article
    article_service.delete_article(article_id)


@pytest.fixture
def article2(shop):
    article = create_article(shop.id, 'item-002', 8)
    article_id = article.id
    yield article
    article_service.delete_article(article_id)


@pytest.fixture
def article3(shop):
    article = create_article(shop.id, 'item-003', 8)
    article_id = article.id
    yield article
    article_service.delete_article(article_id)


@pytest.fixture(scope='module')
def orderer_user(make_user_with_detail):
    return make_user_with_detail('Besteller')


@pytest.fixture(scope='module')
def orderer(orderer_user):
    return create_orderer(orderer_user)


@patch('byceps.signals.shop.order_canceled.send')
@patch('byceps.blueprints.admin.shop.order.views.order_email_service')
def test_cancel_before_paid(
    order_email_service_mock,
    order_canceled_signal_send_mock,
    admin_app,
    storefront,
    article1,
    admin,
    orderer_user,
    orderer,
):
    article = article1

    quantified_articles_to_order = {(article, 3)}
    placed_order = place_order(
        storefront.id, orderer, quantified_articles_to_order
    )
    order_before = get_order(placed_order.id)

    assert get_article_quantity(article.id) == 5

    assert_payment_is_open(order_before)

    url = f'/admin/shop/orders/{order_before.id}/cancel'
    form_data = {
        'reason': 'Dein Vorname ist albern!',
        'send_email': 'y',
    }
    with http_client(admin_app, user_id=admin.id) as client:
        response = client.post(url, data=form_data)

    order_afterwards = get_order(order_before.id)
    assert response.status_code == 302
    assert_payment(
        order_afterwards, None, PaymentState.canceled_before_paid, admin.id
    )

    assert get_article_quantity(article.id) == 8

    order_email_service_mock.send_email_for_canceled_order_to_orderer.assert_called_once_with(
        placed_order.id
    )

    event = ShopOrderCanceled(
        occurred_at=order_afterwards.payment_state_updated_at,
        initiator_id=admin.id,
        initiator_screen_name=admin.screen_name,
        order_id=placed_order.id,
        order_number=placed_order.order_number,
        orderer_id=orderer_user.id,
        orderer_screen_name=orderer_user.screen_name,
    )
    order_canceled_signal_send_mock.assert_called_once_with(None, event=event)

    order_service.delete_order(placed_order.id)


@patch('byceps.signals.shop.order_canceled.send')
@patch('byceps.blueprints.admin.shop.order.views.order_email_service')
def test_cancel_before_paid_without_sending_email(
    order_email_service_mock,
    order_canceled_signal_send_mock,
    admin_app,
    storefront,
    article2,
    admin,
    orderer_user,
    orderer,
):
    article = article2

    quantified_articles_to_order = {(article, 3)}
    placed_order = place_order(
        storefront.id, orderer, quantified_articles_to_order
    )

    url = f'/admin/shop/orders/{placed_order.id}/cancel'
    form_data = {
        'reason': 'Dein Vorname ist albern!',
        # Sending e-mail is not requested.
    }
    with http_client(admin_app, user_id=admin.id) as client:
        response = client.post(url, data=form_data)

    order_afterwards = get_order(placed_order.id)
    assert response.status_code == 302

    # No e-mail should be send.
    order_email_service_mock.send_email_for_canceled_order_to_orderer.assert_not_called()

    event = ShopOrderCanceled(
        occurred_at=order_afterwards.payment_state_updated_at,
        initiator_id=admin.id,
        initiator_screen_name=admin.screen_name,
        order_id=placed_order.id,
        order_number=placed_order.order_number,
        orderer_id=orderer_user.id,
        orderer_screen_name=orderer_user.screen_name,
    )
    order_canceled_signal_send_mock.assert_called_once_with(None, event=event)

    order_service.delete_order(placed_order.id)


@patch('byceps.signals.shop.order_paid.send')
@patch('byceps.blueprints.admin.shop.order.views.order_email_service')
def test_mark_order_as_paid(
    order_email_service_mock,
    order_paid_signal_send_mock,
    admin_app,
    storefront,
    admin,
    orderer_user,
    orderer,
):
    placed_order = place_order(storefront.id, orderer, [])
    order_before = get_order(placed_order.id)

    assert_payment_is_open(order_before)

    url = f'/admin/shop/orders/{order_before.id}/mark_as_paid'
    form_data = {'payment_method': 'direct_debit'}
    with http_client(admin_app, user_id=admin.id) as client:
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
        initiator_id=admin.id,
        initiator_screen_name=admin.screen_name,
        order_id=placed_order.id,
        order_number=placed_order.order_number,
        orderer_id=orderer_user.id,
        orderer_screen_name=orderer_user.screen_name,
        payment_method=PaymentMethod.direct_debit,
    )
    order_paid_signal_send_mock.assert_called_once_with(None, event=event)

    order_service.delete_order(placed_order.id)


@patch('byceps.signals.shop.order_canceled.send')
@patch('byceps.signals.shop.order_paid.send')
@patch('byceps.blueprints.admin.shop.order.views.order_email_service')
def test_cancel_after_paid(
    order_email_service_mock,
    order_paid_signal_send_mock,
    order_canceled_signal_send_mock,
    admin_app,
    storefront,
    article3,
    admin,
    orderer_user,
    orderer,
):
    article = article3

    quantified_articles_to_order = {(article, 3)}
    placed_order = place_order(
        storefront.id, orderer, quantified_articles_to_order
    )
    order_before = get_order(placed_order.id)

    assert get_article_quantity(article.id) == 5

    assert_payment_is_open(order_before)

    url = f'/admin/shop/orders/{order_before.id}/mark_as_paid'
    form_data = {'payment_method': 'bank_transfer'}
    with http_client(admin_app, user_id=admin.id) as client:
        response = client.post(url, data=form_data)

    url = f'/admin/shop/orders/{order_before.id}/cancel'
    form_data = {
        'reason': 'Dein Vorname ist albern!',
        'send_email': 'n',
    }
    with http_client(admin_app, user_id=admin.id) as client:
        response = client.post(url, data=form_data)

    order_afterwards = get_order(order_before.id)
    assert response.status_code == 302
    assert_payment(
        order_afterwards,
        PaymentMethod.bank_transfer,
        PaymentState.canceled_after_paid,
        admin.id,
    )

    assert get_article_quantity(article.id) == 8

    order_email_service_mock.send_email_for_canceled_order_to_orderer.assert_called_once_with(
        placed_order.id
    )

    event = ShopOrderCanceled(
        occurred_at=order_afterwards.payment_state_updated_at,
        initiator_id=admin.id,
        initiator_screen_name=admin.screen_name,
        order_id=placed_order.id,
        order_number=placed_order.order_number,
        orderer_id=orderer_user.id,
        orderer_screen_name=orderer_user.screen_name,
    )
    order_canceled_signal_send_mock.assert_called_once_with(None, event=event)

    order_service.delete_order(placed_order.id)


# helpers


def create_article(shop_id, item_number, total_quantity):
    return _create_article(
        shop_id,
        item_number=item_number,
        description=item_number,
        total_quantity=total_quantity,
    )


def get_article_quantity(article_id):
    article = article_service.get_article(article_id)
    return article.quantity


def place_order(storefront_id, orderer, quantified_articles):
    cart = Cart()

    for article, quantity_to_order in quantified_articles:
        cart.add_item(article, quantity_to_order)

    order, _ = order_service.place_order(storefront_id, orderer, cart)

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
