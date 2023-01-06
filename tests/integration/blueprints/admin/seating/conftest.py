"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from tests.helpers import log_in_user


@pytest.fixture(scope='package')
def seating_admin(make_admin):
    permission_ids = {
        'admin.access',
        'seating.administrate',
        'seating.view',
    }
    admin = make_admin(permission_ids)
    log_in_user(admin.id)
    return admin


@pytest.fixture(scope='package')
def seating_admin_client(make_client, admin_app, seating_admin):
    return make_client(admin_app, user_id=seating_admin.id)
