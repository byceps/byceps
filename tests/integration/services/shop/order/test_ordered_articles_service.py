"""
:Copyright: 2006-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import Flask
import pytest

from byceps.database import db
from byceps.services.shop.article.transfer.models import Article
from byceps.services.shop.cart.models import Cart
from byceps.services.shop.order.dbmodels.order import Order as DbOrder
from byceps.services.shop.order import ordered_articles_service
from byceps.services.shop.order import service as order_service
from byceps.services.shop.order.transfer.number import OrderNumber
from byceps.services.shop.order.transfer.order import (
    Order,
    Orderer,
    PaymentState,
)
from byceps.services.shop.shop.transfer.models import Shop
from byceps.services.shop.storefront.transfer.models import (
    Storefront,
    StorefrontID,
)

from tests.integration.services.shop.helpers import (
    create_article,
    create_orderer,
)


@pytest.fixture
def article(shop: Shop) -> Article:
    return create_article(shop.id, total_quantity=100)


@pytest.fixture
def orderer(make_user) -> Orderer:
    user = make_user()
    return create_orderer(user.id)


def test_count_ordered_articles(
    admin_app: Flask, storefront: Storefront, article: Article, orderer: Orderer
):
    expected = {
        PaymentState.open: 12,
        PaymentState.canceled_before_paid: 7,
        PaymentState.paid: 3,
        PaymentState.canceled_after_paid: 6,
    }

    order_ids = set()
    for article_quantity, payment_state in [
        (4, PaymentState.open),
        (6, PaymentState.canceled_after_paid),
        (1, PaymentState.open),
        (5, PaymentState.canceled_before_paid),
        (3, PaymentState.paid),
        (2, PaymentState.canceled_before_paid),
        (7, PaymentState.open),
    ]:
        order = place_order(
            storefront.id,
            orderer,
            article,
            article_quantity,
        )
        order_ids.add(order.id)
        set_payment_state(order.order_number, payment_state)

    totals = ordered_articles_service.count_ordered_articles(
        article.item_number
    )

    assert totals == expected

    for order_id in order_ids:
        order_service.delete_order(order_id)


# helpers


def place_order(
    storefront_id: StorefrontID,
    orderer: Orderer,
    article: Article,
    article_quantity: int,
) -> Order:
    cart = Cart()
    cart.add_item(article, article_quantity)

    order, _ = order_service.place_order(storefront_id, orderer, cart)

    return order


def set_payment_state(
    order_number: OrderNumber, payment_state: PaymentState
) -> None:
    order = db.session \
        .query(DbOrder) \
        .filter_by(order_number=order_number) \
        .one_or_none()
    order.payment_state = payment_state
    db.session.commit()
