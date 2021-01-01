"""
:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.services.authorization import service


PERMISSION_ID = 'tickle_mortals'


def test_assign_role_to_user(admin_app, user, admin_user, role):
    user_permission_ids_before = service.get_permission_ids_for_user(user.id)
    assert PERMISSION_ID not in user_permission_ids_before

    service.assign_role_to_user(role.id, user.id, initiator_id=admin_user.id)

    user_permission_ids_after = service.get_permission_ids_for_user(user.id)
    assert PERMISSION_ID in user_permission_ids_after

    # Expect attempt to assign that role again to that user to have no
    # effect and to not raise an exception.
    service.assign_role_to_user(role.id, user.id, initiator_id=admin_user.id)


def test_deassign_role_from_user(admin_app, user, admin_user, role):
    service.assign_role_to_user(role.id, user.id, initiator_id=admin_user.id)

    user_permission_ids_before = service.get_permission_ids_for_user(user.id)
    assert PERMISSION_ID in user_permission_ids_before

    service.deassign_role_from_user(
        role.id, user.id, initiator_id=admin_user.id
    )

    user_permission_ids_after = service.get_permission_ids_for_user(user.id)
    assert PERMISSION_ID not in user_permission_ids_after


@pytest.fixture
def permission():
    permission = service.create_permission(PERMISSION_ID, 'Tickle mortals')

    yield permission

    service.delete_permission(permission.id)


@pytest.fixture
def role(permission, user):
    role = service.create_role('demigod', 'Demigod')
    service.assign_permission_to_role(permission.id, role.id)

    yield role

    service.deassign_all_roles_from_user(user.id)
    service.delete_role(role.id)
