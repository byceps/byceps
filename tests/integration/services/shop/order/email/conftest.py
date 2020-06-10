"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import pytest


@pytest.fixture
def order_admin(make_user):
    return make_user('ShopOrderAdmin')
