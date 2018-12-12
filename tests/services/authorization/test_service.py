"""
:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.services.authorization import service as authorization_service

from tests.base import AbstractAppTestCase
from tests.helpers import assign_permissions_to_user


class AuthorizationServiceTestCase(AbstractAppTestCase):

    def test_get_permission_ids_for_user(self):
        user = self.create_user()

        permissions_before = authorization_service.get_permission_ids_for_user(user.id)
        assert permissions_before == frozenset()

        assign_permissions_to_user(user.id, 'board_moderator', {
            'board_topic_hide',
            'board_topic_pin',
        })
        assign_permissions_to_user(user.id, 'news_editor', {
            'news_item_create',
        })

        permissions_after = authorization_service.get_permission_ids_for_user(user.id)
        assert permissions_after == {
            'board_topic_hide',
            'board_topic_pin',
            'news_item_create',
        }
