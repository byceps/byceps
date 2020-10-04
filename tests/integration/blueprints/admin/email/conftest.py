"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import pytest

from tests.helpers import login_user


@pytest.fixture(scope='package')
def email_admin(make_admin):
    permission_ids = {
        'admin.access',
        'email_config.create',
        'email_config.delete',
        'email_config.update',
        'email_config.view',
    }
    admin = make_admin('EmailAdmin', permission_ids)
    login_user(admin.id)
    return admin


@pytest.fixture(scope='package')
def email_admin_client(make_client, admin_app, email_admin):
    return make_client(admin_app, user_id=email_admin.id)
