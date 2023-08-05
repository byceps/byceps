"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.services.authorization import authz_service


PERMISSION_ID = 'board.view_hidden'


def test_assign_role_to_user(admin_app, user, admin_user, role):
    user_permission_ids_before = authz_service.get_permission_ids_for_user(
        user.id
    )
    assert PERMISSION_ID not in user_permission_ids_before

    authz_service.assign_role_to_user(role.id, user.id, initiator=admin_user)

    user_permission_ids_after = authz_service.get_permission_ids_for_user(
        user.id
    )
    assert PERMISSION_ID in user_permission_ids_after

    # Expect attempt to assign that role again to that user to have no
    # effect and to not raise an exception.
    authz_service.assign_role_to_user(role.id, user.id, initiator=admin_user)


def test_deassign_role_from_user(admin_app, user, admin_user, role):
    authz_service.assign_role_to_user(role.id, user.id, initiator=admin_user)

    user_permission_ids_before = authz_service.get_permission_ids_for_user(
        user.id
    )
    assert PERMISSION_ID in user_permission_ids_before

    deassign_result = authz_service.deassign_role_from_user(
        role.id, user.id, initiator=admin_user
    )
    assert deassign_result.is_ok()

    user_permission_ids_after = authz_service.get_permission_ids_for_user(
        user.id
    )
    assert PERMISSION_ID not in user_permission_ids_after


@pytest.fixture()
def role(user):
    role = authz_service.create_role('demigod', 'Demigod').unwrap()
    authz_service.assign_permission_to_role(PERMISSION_ID, role.id)

    yield role

    authz_service.deassign_all_roles_from_user(user.id)
    authz_service.delete_role(role.id)
