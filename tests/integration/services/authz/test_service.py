"""
:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.services.authz import authz_service
from byceps.services.authz.models import PermissionID, RoleID

from tests.helpers import create_role_with_permissions_assigned, generate_token


def test_get_permission_ids_for_user_with_user_permissions(
    database, user, permissions
):
    actual = authz_service.get_permission_ids_for_user(user.id)
    assert actual == {
        'see_everything',
        'tickle_demigods',
        'tickle_mere_mortals',
    }


@pytest.fixture()
def user(make_user):
    return make_user()


@pytest.fixture()
def permissions(user, admin_user):
    role_id_god = RoleID('god_' + generate_token())
    role_id_demigod = RoleID('demigod_' + generate_token())

    create_role_with_permissions_assigned(
        role_id_god,
        {
            PermissionID('see_everything'),
            PermissionID('tickle_demigods'),
        },
    )

    create_role_with_permissions_assigned(
        role_id_demigod,
        {
            PermissionID('tickle_mere_mortals'),
        },
    )

    authz_service.assign_role_to_user(role_id_god, user, initiator=admin_user)
    authz_service.assign_role_to_user(
        role_id_demigod, user, initiator=admin_user
    )
