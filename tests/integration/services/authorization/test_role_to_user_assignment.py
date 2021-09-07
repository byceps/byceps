"""
:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.services.authorization import service


def test_assign_role_to_user(
    admin_app, user, admin_user, permission_tickle_mortals, role
):
    permission_id = permission_tickle_mortals.id

    user_permission_ids_before = service.get_permission_ids_for_user(user.id)
    assert permission_id not in user_permission_ids_before

    service.assign_role_to_user(role.id, user.id, initiator_id=admin_user.id)

    user_permission_ids_after = service.get_permission_ids_for_user(user.id)
    assert permission_id in user_permission_ids_after

    # Expect attempt to assign that role again to that user to have no
    # effect and to not raise an exception.
    service.assign_role_to_user(role.id, user.id, initiator_id=admin_user.id)


def test_deassign_role_from_user(
    admin_app, user, admin_user, permission_tickle_mortals, role
):
    permission_id = permission_tickle_mortals.id

    service.assign_role_to_user(role.id, user.id, initiator_id=admin_user.id)

    user_permission_ids_before = service.get_permission_ids_for_user(user.id)
    assert permission_id in user_permission_ids_before

    service.deassign_role_from_user(
        role.id, user.id, initiator_id=admin_user.id
    )

    user_permission_ids_after = service.get_permission_ids_for_user(user.id)
    assert permission_id not in user_permission_ids_after


@pytest.fixture
def role(permission_tickle_mortals, user):
    role = service.create_role('demigod', 'Demigod')
    service.assign_permission_to_role(permission_tickle_mortals.id, role.id)

    yield role

    service.deassign_all_roles_from_user(user.id)
    service.delete_role(role.id)
