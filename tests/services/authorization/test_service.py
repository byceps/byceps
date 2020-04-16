"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.services.authorization import service as authorization_service

from tests.helpers import assign_permissions_to_user


def test_get_permission_ids_for_user(party_app_with_db, admin_user, user):
    user_id = user.id
    initiator_id = admin_user.id

    permissions_before = authorization_service.get_permission_ids_for_user(
        user_id
    )
    assert permissions_before == frozenset()

    assign_permissions_to_user(user_id, 'god', {
        'see_everything',
        'tickle_demigods',
    }, initiator_id=initiator_id)
    assign_permissions_to_user(user_id, 'demigod', {
        'tickle_mortals',
    }, initiator_id=initiator_id)

    permissions_after = authorization_service.get_permission_ids_for_user(
        user_id
    )
    assert permissions_after == {
        'see_everything',
        'tickle_demigods',
        'tickle_mortals',
    }
