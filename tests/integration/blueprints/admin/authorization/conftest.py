"""
:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.services.authorization import authz_service

from tests.helpers import log_in_user


@pytest.fixture(scope='package')
def role_admin(make_admin):
    permission_ids = {
        'admin.access',
        'role.assign',
        'role.view',
    }
    admin = make_admin(permission_ids)
    log_in_user(admin.id)
    return admin


@pytest.fixture(scope='package')
def role_admin_client(make_client, admin_app, role_admin):
    return make_client(admin_app, user_id=role_admin.id)


@pytest.fixture(scope='module')
def role():
    role_id = 'spin_doctor'
    title = 'Dr. Spin'

    role = authz_service.create_role(role_id, title).unwrap()

    yield role

    authz_service.delete_role(role.id)
