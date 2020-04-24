"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import pytest

from tests.helpers import create_user


@pytest.fixture
def order_admin(party_app):
    return create_user('ShopOrderAdmin')
