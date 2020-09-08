"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import pytest

from tests.helpers import login_user


@pytest.fixture(scope='session')
def email_admin(make_admin):
    permission_ids = {
        'admin.access',
        'email_config.create',
        'email_config.delete',
    }
    admin = make_admin('EmailAdmin', permission_ids)
    login_user(admin.id)
    return admin
