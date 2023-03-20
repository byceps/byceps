"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.services.shop.order import order_payment_service
from byceps.services.shop.shop.models import Shop
from byceps.services.user.models.user import User


pytest.register_assert_rewrite(f'{__package__}.helpers')


@pytest.fixture(scope='package')
def order_admin(make_user):
    return make_user()


@pytest.fixture
def email_payment_instructions_snippets(shop: Shop, order_admin: User) -> None:
    order_payment_service.create_email_payment_instructions(
        shop.id, order_admin.id
    )

    order_payment_service.create_html_payment_instructions(
        shop.id, order_admin.id
    )
