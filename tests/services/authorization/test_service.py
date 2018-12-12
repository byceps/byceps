"""
:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.services.authorization import service as authorization_service

from tests.base import AbstractAppTestCase
from tests.helpers import assign_permissions_to_user


class AuthorizationServiceTestCase(AbstractAppTestCase):

    def setUp(self):
        super().setUp()

        self.user_id = self.create_user().id
        self.initiator_id = self.create_user('Admin').id

    def test_get_permission_ids_for_user(self):
        permissions_before = authorization_service.get_permission_ids_for_user(self.user_id)
        assert permissions_before == frozenset()

        assign_permissions_to_user(self.user_id, 'board_moderator', {
            'board_topic_hide',
            'board_topic_pin',
        }, self.initiator_id)
        assign_permissions_to_user(self.user_id, 'news_editor', {
            'news_item_create',
        }, self.initiator_id)

        permissions_after = authorization_service.get_permission_ids_for_user(self.user_id)
        assert permissions_after == {
            'board_topic_hide',
            'board_topic_pin',
            'news_item_create',
        }
