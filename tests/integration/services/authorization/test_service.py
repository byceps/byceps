"""
:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.services.authorization import authz_service

from tests.helpers import create_role_with_permissions_assigned


def test_get_permission_ids_for_user_without_user_permissions(site_app, user):
    actual = authz_service.get_permission_ids_for_user(user.id)
    assert actual == frozenset()


def test_get_permission_ids_for_user_with_user_permissions(
    site_app, user, permissions
):
    actual = authz_service.get_permission_ids_for_user(user.id)
    assert actual == {
        'see_everything',
        'tickle_demigods',
        'tickle_mere_mortals',
    }


@pytest.fixture
def permissions(user, admin_user):
    role_id_god = 'god'
    role_id_demigod = 'demigod'

    create_role_with_permissions_assigned(
        role_id_god, {'see_everything', 'tickle_demigods'}
    )
    create_role_with_permissions_assigned(
        role_id_demigod, {'tickle_mere_mortals'}
    )

    authz_service.assign_role_to_user(
        role_id_god, user.id, initiator_id=admin_user.id
    )
    authz_service.assign_role_to_user(
        role_id_demigod, user.id, initiator_id=admin_user.id
    )

    yield

    authz_service.deassign_all_roles_from_user(user.id, user.id)

    for role_id in role_id_god, role_id_demigod:
        authz_service.delete_role(role_id)
