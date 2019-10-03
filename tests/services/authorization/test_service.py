"""
:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.services.authorization import service as authorization_service

from tests.helpers import assign_permissions_to_user


def test_get_permission_ids_for_user(
    party_app_with_db, admin_user, normal_user
):
    user_id = normal_user.id
    initiator_id = admin_user.id

    permissions_before = authorization_service \
        .get_permission_ids_for_user(user_id)
    assert permissions_before == frozenset()

    assign_permissions_to_user(user_id, 'board_moderator', {
        'board_topic_hide',
        'board_topic_pin',
    }, initiator_id=initiator_id)
    assign_permissions_to_user(user_id, 'news_editor', {
        'news_item_create',
    }, initiator_id=initiator_id)

    permissions_after = authorization_service \
        .get_permission_ids_for_user(user_id)
    assert permissions_after == {
        'board_topic_hide',
        'board_topic_pin',
        'news_item_create',
    }
