"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from tests.helpers import login_user


@pytest.fixture(scope='package')
def orga_admin(make_admin):
    permission_ids = {
        'admin.access',
        'orga_birthday.view',
        'orga_detail.view',
        'orga_team.administrate_memberships',
    }
    admin = make_admin('OrgaAdmin', permission_ids)
    login_user(admin.id)
    return admin


@pytest.fixture(scope='package')
def orga_admin_client(make_client, admin_app, orga_admin):
    return make_client(admin_app, user_id=orga_admin.id)
