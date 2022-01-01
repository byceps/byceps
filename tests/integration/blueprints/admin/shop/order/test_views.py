"""
:Copyright: 2006-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from typing import Iterable
from unittest.mock import patch

import pytest

from byceps.database import db
from byceps.events.shop import ShopOrderCanceled, ShopOrderPaid
from byceps.services.shop.article import service as article_service
from byceps.services.shop.article.transfer.models import (
    Article,
    ArticleID,
    ArticleNumber,
)
from byceps.services.shop.cart.models import Cart
from byceps.services.shop.order.dbmodels.order import Order as DbOrder
from byceps.services.shop.order import service as order_service
from byceps.services.shop.order.transfer.order import PaymentState
from byceps.services.shop.shop.transfer.models import Shop, ShopID
from byceps.services.shop.storefront.transfer.models import Storefront

from tests.helpers import log_in_user
from tests.integration.services.shop.helpers import (
    create_article as _create_article,
    create_orderer,
)


@pytest.fixture(scope='package')
def shop_order_admin(make_admin):
    permission_ids = {
        'admin.access',
        'shop_order.cancel',
        'shop_order.mark_as_paid',
    }
    admin = make_admin('ShopOrderAdmin', permission_ids)
    log_in_user(admin.id)
    return admin


@pytest.fixture(scope='package')
def shop_order_admin_client(make_client, admin_app, shop_order_admin):
    return make_client(admin_app, user_id=shop_order_admin.id)


@pytest.fixture
def article1(shop: Shop) -> Article:
    return create_article(shop.id, 'item-001', 8)


@pytest.fixture
def article2(shop: Shop) -> Article:
    return create_article(shop.id, 'item-002', 8)


@pytest.fixture
def article3(shop: Shop) -> Article:
    return create_article(shop.id, 'item-003', 8)


@pytest.fixture(scope='module')
def orderer_user(make_user):
    return make_user()


@pytest.fixture(scope='module')
def orderer(orderer_user):
    return create_orderer(orderer_user.id)


@patch('byceps.signals.shop.order_canceled.send')
@patch('byceps.blueprints.admin.shop.order.views.order_email_service')
def test_cancel_before_paid(
    order_email_service_mock,
    order_canceled_signal_send_mock,
    storefront: Storefront,
    article1: Article,
    shop_order_admin,
    orderer_user,
    orderer,
    shop_order_admin_client,
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
    response = shop_order_admin_client.post(url, data=form_data)

    order_afterwards = get_order(order_before.id)
    assert response.status_code == 302
    assert_payment(
        order_afterwards,
        None,
        PaymentState.canceled_before_paid,
        shop_order_admin.id,
    )

    assert get_article_quantity(article.id) == 8

    order_email_service_mock.send_email_for_canceled_order_to_orderer.assert_called_once_with(
        placed_order.id
    )

    event = ShopOrderCanceled(
        occurred_at=order_afterwards.payment_state_updated_at,
        initiator_id=shop_order_admin.id,
        initiator_screen_name=shop_order_admin.screen_name,
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
    storefront: Storefront,
    article2: Article,
    shop_order_admin,
    orderer_user,
    orderer,
    shop_order_admin_client,
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
    response = shop_order_admin_client.post(url, data=form_data)

    order_afterwards = get_order(placed_order.id)
    assert response.status_code == 302

    # No e-mail should be send.
    order_email_service_mock.send_email_for_canceled_order_to_orderer.assert_not_called()

    event = ShopOrderCanceled(
        occurred_at=order_afterwards.payment_state_updated_at,
        initiator_id=shop_order_admin.id,
        initiator_screen_name=shop_order_admin.screen_name,
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
    storefront: Storefront,
    shop_order_admin,
    orderer_user,
    orderer,
    shop_order_admin_client,
):
    placed_order = place_order(storefront.id, orderer, [])
    order_before = get_order(placed_order.id)

    assert_payment_is_open(order_before)

    url = f'/admin/shop/orders/{order_before.id}/mark_as_paid'
    form_data = {'payment_method': 'direct_debit'}
    response = shop_order_admin_client.post(url, data=form_data)

    order_afterwards = get_order(order_before.id)
    assert response.status_code == 302
    assert_payment(
        order_afterwards,
        'direct_debit',
        PaymentState.paid,
        shop_order_admin.id,
    )

    order_email_service_mock.send_email_for_paid_order_to_orderer.assert_called_once_with(
        placed_order.id
    )

    event = ShopOrderPaid(
        occurred_at=order_afterwards.payment_state_updated_at,
        initiator_id=shop_order_admin.id,
        initiator_screen_name=shop_order_admin.screen_name,
        order_id=placed_order.id,
        order_number=placed_order.order_number,
        orderer_id=orderer_user.id,
        orderer_screen_name=orderer_user.screen_name,
        payment_method='direct_debit',
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
    storefront: Storefront,
    article3: Article,
    shop_order_admin,
    orderer_user,
    orderer,
    shop_order_admin_client,
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
    response = shop_order_admin_client.post(url, data=form_data)

    url = f'/admin/shop/orders/{order_before.id}/cancel'
    form_data = {
        'reason': 'Dein Vorname ist albern!',
        'send_email': 'n',
    }
    response = shop_order_admin_client.post(url, data=form_data)

    order_afterwards = get_order(order_before.id)
    assert response.status_code == 302
    assert_payment(
        order_afterwards,
        'bank_transfer',
        PaymentState.canceled_after_paid,
        shop_order_admin.id,
    )

    assert get_article_quantity(article.id) == 8

    order_email_service_mock.send_email_for_canceled_order_to_orderer.assert_called_once_with(
        placed_order.id
    )

    event = ShopOrderCanceled(
        occurred_at=order_afterwards.payment_state_updated_at,
        initiator_id=shop_order_admin.id,
        initiator_screen_name=shop_order_admin.screen_name,
        order_id=placed_order.id,
        order_number=placed_order.order_number,
        orderer_id=orderer_user.id,
        orderer_screen_name=orderer_user.screen_name,
    )
    order_canceled_signal_send_mock.assert_called_once_with(None, event=event)

    order_service.delete_order(placed_order.id)


# helpers


def create_article(
    shop_id: ShopID, item_number: str, total_quantity: int
) -> Article:
    return _create_article(
        shop_id,
        item_number=ArticleNumber(item_number),
        description=item_number,
        total_quantity=total_quantity,
    )


def get_article_quantity(article_id: ArticleID) -> int:
    article = article_service.get_article(article_id)
    return article.quantity


def place_order(
    storefront_id, orderer, quantified_articles: Iterable[tuple[Article, int]]
):
    cart = Cart()

    for article, quantity_to_order in quantified_articles:
        cart.add_item(article, quantity_to_order)

    order, _ = order_service.place_order(storefront_id, orderer, cart)

    return order


def assert_payment_is_open(order) -> None:
    assert order.payment_method is None  # default
    assert order.payment_state == PaymentState.open
    assert order.payment_state_updated_at is None
    assert order.payment_state_updated_by_id is None


def assert_payment(order, method, state, updated_by_id) -> None:
    assert order.payment_method == method
    assert order.payment_state == state
    assert order.payment_state_updated_at is not None
    assert order.payment_state_updated_by_id == updated_by_id


def get_order(order_id):
    return db.session.query(DbOrder).get(order_id)
