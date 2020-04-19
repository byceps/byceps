"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import pytest

from byceps.services.authorization import service as authorization_service

from tests.helpers import assign_permissions_to_user, create_permissions


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

    create_permissions(permission_ids)

    assign_permissions_to_user(
        user.id,
        'god',
        {'see_everything', 'tickle_demigods'},
        initiator_id=admin_user.id,
    )

    assign_permissions_to_user(
        user.id,
        'demigod',
        {'tickle_mortals'},
        initiator_id=admin_user.id
    )

    yield

    authorization_service.deassign_all_roles_from_user(user.id, user.id)

    for role_id in {'god', 'demigod'}:
        authorization_service.delete_role(role_id)

    for permission_id in permission_ids:
        authorization_service.delete_permission(permission_id)
