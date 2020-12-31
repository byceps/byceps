"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from tests.helpers import login_user


@pytest.fixture(scope='package')
def more_admin(make_admin):
    permission_ids = {
        'admin.access',
    }
    admin = make_admin('MoreAdmin', permission_ids)
    login_user(admin.id)
    return admin


@pytest.fixture(scope='package')
def more_admin_client(make_client, admin_app, more_admin):
    return make_client(admin_app, user_id=more_admin.id)
