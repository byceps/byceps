"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import pytest

from byceps.services.authorization import service


PERMISSION_ID = 'tickle_mortals'


def test_assign_role_to_user(admin_app_with_db, user, admin_user, role):
    user_id = user.id
    initiator_id = admin_user.id

    user_permission_ids_before = service.get_permission_ids_for_user(user_id)
    assert PERMISSION_ID not in user_permission_ids_before

    service.assign_role_to_user(role.id, user_id, initiator_id=initiator_id)

    user_permission_ids_after = service.get_permission_ids_for_user(user_id)
    assert PERMISSION_ID in user_permission_ids_after

    # Expect attempt to assign that role again to that user to have no
    # effect and to not raise an exception.
    service.assign_role_to_user(role.id, user_id, initiator_id=initiator_id)


def test_deassign_role_from_user(admin_app_with_db, user, admin_user, role):
    user_id = user.id
    initiator_id = admin_user.id

    service.assign_role_to_user(role.id, user_id, initiator_id=initiator_id)

    user_permission_ids_before = service.get_permission_ids_for_user(user_id)
    assert PERMISSION_ID in user_permission_ids_before

    service.deassign_role_from_user(role.id, user_id, initiator_id=initiator_id)

    user_permission_ids_after = service.get_permission_ids_for_user(user_id)
    assert PERMISSION_ID not in user_permission_ids_after


@pytest.fixture
def permission():
    return service.create_permission(PERMISSION_ID, 'Tickle mortals')


@pytest.fixture
def role(permission):
    role = service.create_role('demigod', 'Demigod')
    service.assign_permission_to_role(permission.id, role.id)
    return role
