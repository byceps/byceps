"""
:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from moneyed import EUR

from byceps.services.authentication.session.models.current_user import (
    CurrentUser,
)
from byceps.services.authentication.session import authn_session_service
from byceps.services.shop.cart.models import Cart
from byceps.services.shop.order import order_service
from byceps.services.user.transfer.models import User


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

    order, _ = order_service.place_order(
        storefront_id, orderer, cart, created_at=created_at
    )

    return order


def assert_email(
    mock, expected_sender, expected_recipients, expected_subject, expected_body
):
    calls = mock.call_args_list
    assert len(calls) == 1

    pos_args, _ = calls[0]
    actual_sender, actual_recipients, actual_subject, actual_body = pos_args
    assert actual_sender == expected_sender
    assert actual_recipients == expected_recipients
    assert actual_subject == expected_subject
    assert actual_body == expected_body
