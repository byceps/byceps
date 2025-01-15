"""
:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest
from sqlalchemy import select

from byceps.byceps_app import BycepsApp
from byceps.database import db
from byceps.services.shop.order import ordered_products_service
from byceps.services.shop.order.dbmodels.order import DbOrder
from byceps.services.shop.order.models.number import OrderNumber
from byceps.services.shop.order.models.order import Orderer, PaymentState
from byceps.services.shop.product.models import Product
from byceps.services.shop.shop.models import Shop
from byceps.services.shop.storefront.models import Storefront

from tests.helpers.shop import place_order


@pytest.fixture()
def product(make_product, shop: Shop) -> Product:
    return make_product(shop.id)


@pytest.fixture()
def orderer(make_user, make_orderer) -> Orderer:
    user = make_user()
    return make_orderer(user)


def test_count_ordered_products(
    admin_app: BycepsApp,
    shop: Shop,
    storefront: Storefront,
    product: Product,
    orderer: Orderer,
):
    expected = {
        PaymentState.open: 12,
        PaymentState.canceled_before_paid: 7,
        PaymentState.paid: 3,
        PaymentState.canceled_after_paid: 6,
    }

    order_ids = set()
    for product_quantity, payment_state in [
        (4, PaymentState.open),
        (6, PaymentState.canceled_after_paid),
        (1, PaymentState.open),
        (5, PaymentState.canceled_before_paid),
        (3, PaymentState.paid),
        (2, PaymentState.canceled_before_paid),
        (7, PaymentState.open),
    ]:
        order = place_order(
            shop,
            storefront,
            orderer,
            [(product, product_quantity)],
        )
        order_ids.add(order.id)
        set_payment_state(order.order_number, payment_state)

    totals = ordered_products_service.count_ordered_products(product.id)

    assert totals == expected


# helpers


def set_payment_state(
    order_number: OrderNumber, payment_state: PaymentState
) -> None:
    order = db.session.execute(
        select(DbOrder).filter_by(order_number=order_number)
    ).scalar_one()
    order.payment_state = payment_state
    db.session.commit()
