"""
:Copyright: 2014-2024 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.services.authz import authz_service


def test_deassign_all_roles_from_user(
    admin_app, user1, user2, role1, role2, role3
):
    assert authz_service.find_role_ids_for_user(user1.id) == {
        role1.id,
        role2.id,
    }
    assert authz_service.find_role_ids_for_user(user2.id) == {
        role1.id,
        role3.id,
    }

    authz_service.deassign_all_roles_from_user(user1)

    # Targeted user's roles should have been deassigned.
    assert authz_service.find_role_ids_for_user(user1.id) == set()
    # All other users' roles should still be assigned.
    assert authz_service.find_role_ids_for_user(user2.id) == {
        role1.id,
        role3.id,
    }


@pytest.fixture()
def user1(make_user):
    return make_user()


@pytest.fixture()
def user2(make_user):
    return make_user()


@pytest.fixture()
def role1(make_role, user1, user2, admin_user):
    role = make_role()

    authz_service.assign_role_to_user(role.id, user1, initiator=admin_user)
    authz_service.assign_role_to_user(role.id, user2, initiator=admin_user)

    return role


@pytest.fixture()
def role2(make_role, user1, admin_user):
    role = make_role()

    authz_service.assign_role_to_user(role.id, user1, initiator=admin_user)

    return role


@pytest.fixture()
def role3(make_role, user2, admin_user):
    role = make_role()

    authz_service.assign_role_to_user(role.id, user2, initiator=admin_user)

    return role
