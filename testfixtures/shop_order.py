"""
testfixtures.shop_order
~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.services.shop.order.models import Order, Orderer, OrderItem, \
    PaymentMethod


ANY_ORDER_NUMBER = 'AEC-03-B00074'


def create_orderer(user):
    return Orderer(
        user,
        user.detail.first_names,
        user.detail.last_name,
        user.detail.date_of_birth,
        user.detail.country,
        user.detail.zip_code,
        user.detail.city,
        user.detail.street)


def create_order(party_id, placed_by, *, order_number=ANY_ORDER_NUMBER,
                 payment_method=PaymentMethod.bank_transfer,
                 shipping_required=False):
    order = Order(
        party_id,
        order_number,
        placed_by,
        placed_by.detail.first_names,
        placed_by.detail.last_name,
        placed_by.detail.date_of_birth,
        placed_by.detail.country,
        placed_by.detail.zip_code,
        placed_by.detail.city,
        placed_by.detail.street,
        payment_method,
    )

    order.shipping_required = shipping_required

    return order


def create_order_item(order, article, quantity):
    return OrderItem(order, article, quantity)
