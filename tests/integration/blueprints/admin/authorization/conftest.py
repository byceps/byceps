"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import pytest

import byceps.services.authorization.service as authz_service

from tests.helpers import login_user


@pytest.fixture(scope='package')
def role_admin(make_admin):
    permission_ids = {
        'admin.access',
        'role.assign',
        'role.view',
    }
    admin = make_admin('RoleAdmin', permission_ids)
    login_user(admin.id)
    return admin


@pytest.fixture(scope='package')
def role_admin_client(make_client, admin_app, role_admin):
    return make_client(admin_app, user_id=role_admin.id)


@pytest.fixture(scope='module')
def permission():
    permission_id = 'spin_around'
    title = 'Spin around'

    permission = authz_service.create_permission(permission_id, title)

    yield permission

    authz_service.delete_permission(permission.id)


@pytest.fixture(scope='module')
def role():
    role_id = 'spin_doctor'
    title = 'Dr. Spin'

    role = authz_service.create_role(role_id, title)

    yield role

    authz_service.delete_role(role.id)
