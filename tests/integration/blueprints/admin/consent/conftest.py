"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import pytest

from tests.helpers import login_user


@pytest.fixture(scope='package')
def consent_admin(make_admin):
    permission_ids = {
        'admin.access',
        'consent.administrate',
    }
    admin = make_admin('ConsentAdmin', permission_ids)
    login_user(admin.id)
    return admin


@pytest.fixture(scope='package')
def consent_admin_client(make_client, admin_app, consent_admin):
    return make_client(admin_app, user_id=consent_admin.id)
