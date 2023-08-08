"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import Flask
from moneyed import EUR
import pytest
from sqlalchemy import select

from byceps.database import db
from byceps.services.shop.article.models import Article
from byceps.services.shop.cart.models import Cart
from byceps.services.shop.order import (
    order_checkout_service,
    ordered_articles_service,
)
from byceps.services.shop.order.dbmodels.order import DbOrder
from byceps.services.shop.order.models.number import OrderNumber
from byceps.services.shop.order.models.order import Order, Orderer, PaymentState
from byceps.services.shop.shop.models import Shop
from byceps.services.shop.storefront.models import Storefront


@pytest.fixture()
def article(make_article, shop: Shop) -> Article:
    return make_article(shop.id)


@pytest.fixture()
def orderer(make_user, make_orderer) -> Orderer:
    user = make_user()
    return make_orderer(user)


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
            storefront,
            orderer,
            article,
            article_quantity,
        )
        order_ids.add(order.id)
        set_payment_state(order.order_number, payment_state)

    totals = ordered_articles_service.count_ordered_articles(article.id)

    assert totals == expected


# helpers


def place_order(
    storefront: Storefront,
    orderer: Orderer,
    article: Article,
    article_quantity: int,
) -> Order:
    cart = Cart(EUR)
    cart.add_item(article, article_quantity)

    order, _ = order_checkout_service.place_order(
        storefront, orderer, cart
    ).unwrap()

    return order


def set_payment_state(
    order_number: OrderNumber, payment_state: PaymentState
) -> None:
    order = db.session.execute(
        select(DbOrder).filter_by(order_number=order_number)
    ).scalar_one()
    order.payment_state = payment_state
    db.session.commit()
