"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Iterable, Optional
from unittest.mock import patch

from flask import Flask
from moneyed import EUR
import pytest

from byceps.database import db
from byceps.events.shop import ShopOrderCanceled, ShopOrderPaid
from byceps.services.shop.article import article_service
from byceps.services.shop.article.transfer.models import (
    Article,
    ArticleID,
    ArticleNumber,
)
from byceps.services.shop.cart.models import Cart
from byceps.services.shop.order.dbmodels.order import DbOrder
from byceps.services.shop.order import order_service
from byceps.services.shop.order.transfer.order import (
    Order,
    Orderer,
    OrderID,
    PaymentState,
)
from byceps.services.shop.shop.transfer.models import Shop
from byceps.services.shop.storefront.transfer.models import (
    Storefront,
    StorefrontID,
)
from byceps.services.user.transfer.models import User
from byceps.typing import UserID

from tests.helpers import log_in_user


@pytest.fixture(scope='package')
def shop_order_admin(make_admin) -> User:
    permission_ids = {
        'admin.access',
        'shop_order.cancel',
        'shop_order.mark_as_paid',
    }
    admin = make_admin(permission_ids)
    log_in_user(admin.id)
    return admin


@pytest.fixture(scope='package')
def shop_order_admin_client(
    make_client, admin_app: Flask, shop_order_admin: User
):
    return make_client(admin_app, user_id=shop_order_admin.id)


@pytest.fixture
def article1(make_article, shop: Shop) -> Article:
    return make_article(
        shop.id,
        item_number=ArticleNumber('item-001'),
        description='Item #1',
        total_quantity=8,
    )


@pytest.fixture
def article2(make_article, shop: Shop) -> Article:
    return make_article(
        shop.id,
        item_number=ArticleNumber('item-002'),
        description='Item #2',
        total_quantity=8,
    )


@pytest.fixture
def article3(make_article, shop: Shop) -> Article:
    return make_article(
        shop.id,
        item_number=ArticleNumber('item-003'),
        description='Item #3',
        total_quantity=8,
    )


@pytest.fixture(scope='module')
def orderer_user(make_user) -> User:
    return make_user()


@pytest.fixture(scope='module')
def orderer(make_orderer, orderer_user: User) -> Orderer:
    return make_orderer(orderer_user.id)


@patch('byceps.signals.shop.order_canceled.send')
@patch('byceps.blueprints.admin.shop.order.views.order_email_service')
def test_cancel_before_paid(
    order_email_service_mock,
    order_canceled_signal_send_mock,
    storefront: Storefront,
    article1: Article,
    shop_order_admin: User,
    orderer_user: User,
    orderer: Orderer,
    shop_order_admin_client,
):
    article = article1

    quantified_articles_to_order = [(article, 3)]
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


@patch('byceps.signals.shop.order_canceled.send')
@patch('byceps.blueprints.admin.shop.order.views.order_email_service')
def test_cancel_before_paid_without_sending_email(
    order_email_service_mock,
    order_canceled_signal_send_mock,
    storefront: Storefront,
    article2: Article,
    shop_order_admin: User,
    orderer_user: User,
    orderer: Orderer,
    shop_order_admin_client,
):
    article = article2

    quantified_articles_to_order = [(article, 3)]
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


@patch('byceps.signals.shop.order_paid.send')
@patch('byceps.blueprints.admin.shop.order.views.order_email_service')
def test_mark_order_as_paid(
    order_email_service_mock,
    order_paid_signal_send_mock,
    storefront: Storefront,
    shop_order_admin: User,
    orderer_user: User,
    orderer: Orderer,
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


@patch('byceps.signals.shop.order_canceled.send')
@patch('byceps.signals.shop.order_paid.send')
@patch('byceps.blueprints.admin.shop.order.views.order_email_service')
def test_cancel_after_paid(
    order_email_service_mock,
    order_paid_signal_send_mock,
    order_canceled_signal_send_mock,
    storefront: Storefront,
    article3: Article,
    shop_order_admin: User,
    orderer_user: User,
    orderer: Orderer,
    shop_order_admin_client,
):
    article = article3

    quantified_articles_to_order = [(article, 3)]
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


# helpers


def get_article_quantity(article_id: ArticleID) -> int:
    article = article_service.get_article(article_id)
    return article.quantity


def place_order(
    storefront_id: StorefrontID,
    orderer: Orderer,
    quantified_articles: Iterable[tuple[Article, int]],
) -> Order:
    cart = Cart(EUR)

    for article, quantity_to_order in quantified_articles:
        cart.add_item(article, quantity_to_order)

    order, _ = order_service.place_order(storefront_id, orderer, cart)

    return order


def assert_payment_is_open(order: DbOrder) -> None:
    assert order.payment_method is None  # default
    assert order.payment_state == PaymentState.open
    assert order.payment_state_updated_at is None
    assert order.payment_state_updated_by_id is None


def assert_payment(
    order: DbOrder,
    method: Optional[str],
    state: PaymentState,
    updated_by_id: UserID,
) -> None:
    assert order.payment_method == method
    assert order.payment_state == state
    assert order.payment_state_updated_at is not None
    assert order.payment_state_updated_by_id == updated_by_id


def get_order(order_id: OrderID) -> DbOrder:
    return db.session.get(DbOrder, order_id)
