"""
testfixtures.shop_order
~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from decimal import Decimal

from byceps.services.shop.order.models.order import Order
from byceps.services.shop.order.models.orderer import Orderer


ANY_ORDER_NUMBER = 'AEC-03-B00074'


def create_orderer(user):
    return Orderer(
        user.id,
        user.detail.first_names,
        user.detail.last_name,
        user.detail.country,
        user.detail.zip_code,
        user.detail.city,
        user.detail.street,
    )


def create_order(
    shop_id,
    placed_by,
    *,
    order_number=ANY_ORDER_NUMBER,
    total_amount=None,
    shipping_required=False,
):
    if total_amount is None:
        total_amount = Decimal('23.42')

    order = Order(
        shop_id,
        order_number,
        placed_by.id,
        placed_by.detail.first_names,
        placed_by.detail.last_name,
        placed_by.detail.country,
        placed_by.detail.zip_code,
        placed_by.detail.city,
        placed_by.detail.street,
    )

    order.total_amount = total_amount
    order.shipping_required = shipping_required

    return order
