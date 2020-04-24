"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import pytest

from byceps.services.user import command_service as user_command_service

from tests.helpers import create_user


@pytest.fixture
def order_admin(party_app):
    user = create_user('ShopOrderAdmin')
    user_id = user.id
    yield user
    user_command_service.delete_account(user_id, user_id, 'clean up')
