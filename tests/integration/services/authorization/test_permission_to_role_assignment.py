"""
:Copyright: 2006-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.services.authorization import service


PERMISSION_ID = 'board.view_hidden'


def test_assign_permission_to_role(admin_app, role):
    role_permission_ids_before = get_permission_ids_for_role(role)
    assert PERMISSION_ID not in role_permission_ids_before

    service.assign_permission_to_role(PERMISSION_ID, role.id)

    role_permission_ids_after = get_permission_ids_for_role(role)
    assert PERMISSION_ID in role_permission_ids_after


def test_deassign_permission_from_role(admin_app, role):
    service.assign_permission_to_role(PERMISSION_ID, role.id)

    role_permission_ids_before = get_permission_ids_for_role(role)
    assert PERMISSION_ID in role_permission_ids_before

    service.deassign_permission_from_role(PERMISSION_ID, role.id)

    role_permission_ids_after = get_permission_ids_for_role(role)
    assert PERMISSION_ID not in role_permission_ids_after


@pytest.fixture
def role():
    role = service.create_role('demigod', 'Demigod')
    yield role
    service.delete_role(role.id)


def get_permission_ids_for_role(role):
    return service.get_permission_ids_for_role(role.id)
