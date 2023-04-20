"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.services.authorization import authz_service


def test_deassign_all_roles_from_user(admin_app, user1, user2, roles):
    assert authz_service.find_role_ids_for_user(user1.id) == {
        'demigod',
        'pausenclown',
    }
    assert authz_service.find_role_ids_for_user(user2.id) == {
        'demigod',
        'partymeister',
    }

    authz_service.deassign_all_roles_from_user(user1.id)

    # Targeted user's roles should have been deassigned.
    assert authz_service.find_role_ids_for_user(user1.id) == set()
    # All other users' roles should still be assigned.
    assert authz_service.find_role_ids_for_user(user2.id) == {
        'demigod',
        'partymeister',
    }


@pytest.fixture()
def user1(make_user):
    return make_user()


@pytest.fixture()
def user2(make_user):
    return make_user()


@pytest.fixture()
def roles(user1, user2, admin_user):
    role1 = authz_service.create_role('demigod', 'Demigod').unwrap()
    role2 = authz_service.create_role('pausenclown', 'Pausenclown').unwrap()
    role3 = authz_service.create_role('partymeister', 'Partymeister').unwrap()

    authz_service.assign_role_to_user(
        role1.id, user1.id, initiator_id=admin_user.id
    )
    authz_service.assign_role_to_user(
        role2.id, user1.id, initiator_id=admin_user.id
    )

    authz_service.assign_role_to_user(
        role1.id, user2.id, initiator_id=admin_user.id
    )
    authz_service.assign_role_to_user(
        role3.id, user2.id, initiator_id=admin_user.id
    )

    yield

    for user in user1, user2:
        authz_service.deassign_all_roles_from_user(user.id)

    for role_id in 'demigod', 'pausenclown', 'partymeister':
        authz_service.delete_role(role_id)
