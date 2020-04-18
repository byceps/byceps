"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.services.shop.cart.models import Cart
from byceps.services.shop.order import ordered_articles_service
from byceps.services.shop.order.models.order import Order as DbOrder
from byceps.services.shop.order import service as order_service
from byceps.services.shop.order.transfer.models import PaymentState
from byceps.services.shop.sequence import service as sequence_service

from tests.services.shop.helpers import create_article


def test_count_ordered_articles(admin_app_with_db, db, shop, orderer):
    expected = {
        PaymentState.open: 12,
        PaymentState.canceled_before_paid: 7,
        PaymentState.paid: 3,
        PaymentState.canceled_after_paid: 6,
    }

    sequence_service.create_order_number_sequence(shop.id, 'ABC-01-B')

    article = create_article(shop.id, quantity=100)

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
            shop.id,
            orderer,
            article,
            article_quantity,
        )
        order_ids.add(order.id)
        set_payment_state(db, order.order_number, payment_state)

    totals = ordered_articles_service.count_ordered_articles(
        article.item_number
    )

    assert totals == expected

    for order_id in order_ids:
        order_service.delete_order(order_id)


def place_order(shop_id, orderer, article, article_quantity):
    cart = Cart()
    cart.add_item(article, article_quantity)

    order, _ = order_service.place_order(shop_id, orderer, cart)

    return order


def set_payment_state(db, order_number, payment_state):
    order = DbOrder.query \
        .filter_by(order_number=order_number) \
        .one_or_none()
    order.payment_state = payment_state
    db.session.commit()
