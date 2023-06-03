"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from moneyed import EUR

from byceps.services.authentication.session import authn_session_service
from byceps.services.authentication.session.models import CurrentUser
from byceps.services.shop.cart.models import Cart
from byceps.services.shop.order import order_checkout_service
from byceps.services.user.models.user import User


def get_current_user_for_user(user: User, locale: str) -> CurrentUser:
    return authn_session_service.get_authenticated_current_user(
        user, locale=locale, permissions=frozenset()
    )


def place_order_with_items(
    storefront_id, orderer, created_at=None, items_with_quantity=None
):
    cart = Cart(EUR)

    if items_with_quantity is not None:
        for article, quantity in items_with_quantity:
            cart.add_item(article, quantity)

    order, _ = order_checkout_service.place_order(
        storefront_id, orderer, cart, created_at=created_at
    ).unwrap()

    return order
