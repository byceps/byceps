"""
:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from tests.helpers import log_in_user


@pytest.fixture(scope='package')
def brand_admin(make_admin):
    permission_ids = {
        'admin.access',
        'brand.create',
        'brand.update',
        'brand.view',
    }
    admin = make_admin(permission_ids)
    log_in_user(admin.id)
    return admin


@pytest.fixture(scope='package')
def brand_admin_client(make_client, admin_app, brand_admin):
    return make_client(admin_app, user_id=brand_admin.id)
