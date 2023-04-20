"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.services.authorization import authz_service


PERMISSION_ID = 'board.view_hidden'


def test_assign_permission_to_role(admin_app, role):
    role_permission_ids_before = get_permission_ids_for_role(role)
    assert PERMISSION_ID not in role_permission_ids_before

    authz_service.assign_permission_to_role(PERMISSION_ID, role.id)

    role_permission_ids_after = get_permission_ids_for_role(role)
    assert PERMISSION_ID in role_permission_ids_after


def test_deassign_permission_from_role(admin_app, role):
    authz_service.assign_permission_to_role(PERMISSION_ID, role.id)

    role_permission_ids_before = get_permission_ids_for_role(role)
    assert PERMISSION_ID in role_permission_ids_before

    deassign_result = authz_service.deassign_permission_from_role(
        PERMISSION_ID, role.id
    )
    assert deassign_result.is_ok()

    role_permission_ids_after = get_permission_ids_for_role(role)
    assert PERMISSION_ID not in role_permission_ids_after


@pytest.fixture()
def role():
    role = authz_service.create_role('demigod', 'Demigod').unwrap()
    yield role
    authz_service.delete_role(role.id)


def get_permission_ids_for_role(role):
    return authz_service.get_permission_ids_for_role(role.id)
