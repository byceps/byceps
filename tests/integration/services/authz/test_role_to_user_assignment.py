"""
:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.services.authz import authz_service

from tests.helpers import generate_token


def test_assign_role_to_user(admin_app, user, admin_user, role):
    permission_id = generate_token()
    authz_service.assign_permission_to_role(permission_id, role.id)

    user_permission_ids_before = authz_service.get_permission_ids_for_user(
        user.id
    )
    assert permission_id not in user_permission_ids_before

    authz_service.assign_role_to_user(role.id, user, initiator=admin_user)

    user_permission_ids_after = authz_service.get_permission_ids_for_user(
        user.id
    )
    assert permission_id in user_permission_ids_after

    # Expect attempt to assign that role again to that user to have no
    # effect and to not raise an exception.
    authz_service.assign_role_to_user(role.id, user, initiator=admin_user)


def test_deassign_role_from_user(admin_app, user, admin_user, role):
    permission_id = generate_token()
    authz_service.assign_permission_to_role(permission_id, role.id)

    authz_service.assign_role_to_user(role.id, user, initiator=admin_user)

    user_permission_ids_before = authz_service.get_permission_ids_for_user(
        user.id
    )
    assert permission_id in user_permission_ids_before

    deassign_result = authz_service.deassign_role_from_user(
        role.id, user, initiator=admin_user
    )
    assert deassign_result.is_ok()

    user_permission_ids_after = authz_service.get_permission_ids_for_user(
        user.id
    )
    assert permission_id not in user_permission_ids_after


@pytest.fixture()
def role(make_role):
    return make_role()
