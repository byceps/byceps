"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import pytest

from tests.helpers import login_user


@pytest.fixture(scope='module')
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
