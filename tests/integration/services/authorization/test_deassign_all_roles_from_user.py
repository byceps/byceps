"""
:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.services.authorization import service as authorization_service
from byceps.services.authorization.service import (
    assign_role_to_user,
    create_role,
    deassign_all_roles_from_user,
    delete_role,
    find_role_ids_for_user,
)
from byceps.services.user import command_service as user_command_service


def test_deassign_all_roles_from_user(admin_app, user1, user2, roles):
    assert find_role_ids_for_user(user1.id) == {'demigod', 'pausenclown'}
    assert find_role_ids_for_user(user2.id) == {'demigod', 'partymeister'}

    deassign_all_roles_from_user(user1.id)

    # Targeted user's roles should have been deassigned.
    assert find_role_ids_for_user(user1.id) == set()
    # All other users' roles should still be assigned.
    assert find_role_ids_for_user(user2.id) == {'demigod', 'partymeister'}


@pytest.fixture
def user1(make_user):
    return make_user()


@pytest.fixture
def user2(make_user):
    return make_user()


@pytest.fixture
def roles(user1, user2, admin_user):
    role1 = create_role('demigod', 'Demigod')
    role2 = create_role('pausenclown', 'Pausenclown')
    role3 = create_role('partymeister', 'Partymeister')

    assign_role_to_user(role1.id, user1.id, initiator_id=admin_user.id)
    assign_role_to_user(role2.id, user1.id, initiator_id=admin_user.id)

    assign_role_to_user(role1.id, user2.id, initiator_id=admin_user.id)
    assign_role_to_user(role3.id, user2.id, initiator_id=admin_user.id)

    yield

    for user in user1, user2:
        deassign_all_roles_from_user(user.id)

    for role_id in 'demigod', 'pausenclown', 'partymeister':
        delete_role(role_id)
