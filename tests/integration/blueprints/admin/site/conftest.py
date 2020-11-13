"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from tests.helpers import login_user


@pytest.fixture(scope='package')
def site_admin(make_admin):
    permission_ids = {
        'admin.access',
        'site.create',
        'site.update',
        'site.view',
    }
    admin = make_admin('SiteAdmin', permission_ids)
    login_user(admin.id)
    return admin


@pytest.fixture(scope='package')
def site_admin_client(make_client, admin_app, site_admin):
    return make_client(admin_app, user_id=site_admin.id)
