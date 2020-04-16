"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.services.authorization.service import (
    assign_role_to_user,
    create_role,
    deassign_all_roles_from_user,
    find_role_ids_for_user,
)

from tests.helpers import create_user


def test_deassign_all_roles_from_user(admin_app_with_db, admin_user):
    role1 = create_role('demigod', 'Demigod')
    role2 = create_role('pausenclown', 'Pausenclown')
    role3 = create_role('partymeister', 'Partymeister')

    user1 = create_user('User1')
    user2 = create_user('User2')

    initiator_id = admin_user.id
    assign_role_to_user(role1.id, user1.id, initiator_id=admin_user)
    assign_role_to_user(role2.id, user1.id, initiator_id=admin_user)
    assign_role_to_user(role1.id, user2.id, initiator_id=admin_user)
    assign_role_to_user(role3.id, user2.id, initiator_id=admin_user)

    assert find_role_ids_for_user(user1.id) == {'demigod', 'pausenclown'}
    assert find_role_ids_for_user(user2.id) == {'demigod', 'partymeister'}

    deassign_all_roles_from_user(user1.id)

    # Targeted user's roles should have been deassigned.
    assert find_role_ids_for_user(user1.id) == set()
    # All other users' roles should still be assigned.
    assert find_role_ids_for_user(user2.id) == {'demigod', 'partymeister'}
