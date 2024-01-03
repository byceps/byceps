"""
:Copyright: 2014-2024 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.services.authz import authz_service

from tests.helpers import generate_token


def test_assign_permission_to_role(admin_app, role):
    permission_id = generate_token()

    role_permission_ids_before = get_permission_ids_for_role(role)
    assert permission_id not in role_permission_ids_before

    authz_service.assign_permission_to_role(permission_id, role.id)

    role_permission_ids_after = get_permission_ids_for_role(role)
    assert permission_id in role_permission_ids_after


def test_deassign_permission_from_role(admin_app, role):
    permission_id = generate_token()

    authz_service.assign_permission_to_role(permission_id, role.id)

    role_permission_ids_before = get_permission_ids_for_role(role)
    assert permission_id in role_permission_ids_before

    deassign_result = authz_service.deassign_permission_from_role(
        permission_id, role.id
    )
    assert deassign_result.is_ok()

    role_permission_ids_after = get_permission_ids_for_role(role)
    assert permission_id not in role_permission_ids_after


@pytest.fixture(scope='module')
def role(make_role):
    return make_role()


def get_permission_ids_for_role(role):
    return authz_service.get_permission_ids_for_role(role.id)
