"""
:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.services.authentication.session.models.current_user import (
    CurrentUser,
)
from byceps.services.authentication.session import service as session_service
from byceps.services.shop.cart.models import Cart
from byceps.services.shop.order import service as order_service

from tests.integration.services.shop.helpers import create_orderer


def get_current_user_for_user(user) -> CurrentUser:
    return session_service.get_authenticated_current_user(
        user, locale=None, permissions=frozenset()
    )


def place_order_with_items(
    storefront_id, user, created_at=None, items_with_quantity=None
):
    orderer = create_orderer(user.id)

    cart = Cart()

    if items_with_quantity is not None:
        for article, quantity in items_with_quantity:
            cart.add_item(article, quantity)

    order, _ = order_service.place_order(
        storefront_id, orderer, cart, created_at=created_at
    )

    return order
