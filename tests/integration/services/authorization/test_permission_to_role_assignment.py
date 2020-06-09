"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import pytest

from byceps.services.authorization import service


def test_assign_permission_to_role(admin_app, permission, role):
    role_permission_ids_before = get_permission_ids_for_role(role)
    assert permission.id not in role_permission_ids_before

    service.assign_permission_to_role(permission.id, role.id)

    role_permission_ids_after = get_permission_ids_for_role(role)
    assert permission.id in role_permission_ids_after

    # Clean up.
    service.deassign_permission_from_role(permission.id, role.id)


def test_deassign_permission_from_role(admin_app, permission, role):
    service.assign_permission_to_role(permission.id, role.id)

    role_permission_ids_before = get_permission_ids_for_role(role)
    assert permission.id in role_permission_ids_before

    service.deassign_permission_from_role(permission.id, role.id)

    role_permission_ids_after = get_permission_ids_for_role(role)
    assert permission.id not in role_permission_ids_after


@pytest.fixture
def permission():
    permission = service.create_permission('tickle_mortals', 'Tickle mortals')
    yield permission
    service.delete_permission(permission.id)


@pytest.fixture
def role():
    role = service.create_role('demigod', 'Demigod')
    yield role
    service.delete_role(role.id)


def get_permission_ids_for_role(role):
    return {p.id for p in role.permissions}
