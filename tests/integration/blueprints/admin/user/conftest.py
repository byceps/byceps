"""
:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from tests.helpers import log_in_user


@pytest.fixture(scope='package')
def user_admin(make_admin):
    permission_ids = {
        'admin.access',
        'role.assign',
        'user.administrate',
        'user.create',
        'user.set_password',
        'user.view',
    }
    admin = make_admin('UserAdmin', permission_ids)
    log_in_user(admin.id)
    return admin


@pytest.fixture(scope='package')
def user_admin_client(make_client, admin_app, user_admin):
    return make_client(admin_app, user_id=user_admin.id)
