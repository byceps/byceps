"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import pytest

from byceps.services.authorization import service as authorization_service

from tests.helpers import (
    create_permissions,
    create_role_with_permissions_assigned,
)


def test_get_permission_ids_for_user_without_user_permissions(
    party_app_with_db, user
):
    actual = authorization_service.get_permission_ids_for_user(user.id)
    assert actual == frozenset()


def test_get_permission_ids_for_user_with_user_permissions(
    party_app_with_db, user, permissions
):
    actual = authorization_service.get_permission_ids_for_user(user.id)
    assert actual == {
        'see_everything',
        'tickle_demigods',
        'tickle_mortals',
    }


@pytest.fixture
def permissions(user, admin_user):
    permission_ids = {
        'see_everything',
        'tickle_demigods',
        'tickle_mortals',
    }
    role_id_god = 'god'
    role_id_demigod = 'demigod'

    create_permissions(permission_ids)

    create_role_with_permissions_assigned(
        role_id_god, {'see_everything', 'tickle_demigods'}
    )
    create_role_with_permissions_assigned(role_id_demigod, {'tickle_mortals'})

    authorization_service.assign_role_to_user(
        role_id_god, user.id, initiator_id=admin_user.id
    )
    authorization_service.assign_role_to_user(
        role_id_demigod, user.id, initiator_id=admin_user.id
    )

    yield

    authorization_service.deassign_all_roles_from_user(user.id, user.id)

    for role_id in role_id_god, role_id_demigod:
        authorization_service.delete_role(role_id)

    for permission_id in permission_ids:
        authorization_service.delete_permission(permission_id)
