"""
:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.services.board import topic_service as board_topic_service

from .topic_moderation_base import AbstractTopicModerationTest


class TopicPinTest(AbstractTopicModerationTest):

    def setUp(self):
        super().setUp()

        self.setup_admin_with_permission('board_topic.lock')

        self.category_id = self.create_category(1).id

    def test_lock_topic(self):
        topic_before = self.create_topic(self.category_id, self.user.id, 1)

        assert not topic_before.locked
        assert topic_before.locked_at is None
        assert topic_before.locked_by_id is None

        url = '/board/topics/{}/flags/locked'.format(topic_before.id)
        with self.client(user=self.admin) as client:
            response = client.post(url)

        assert response.status_code == 204
        topic_afterwards = self.find_topic(topic_before.id)
        assert topic_afterwards.locked
        assert topic_afterwards.locked_at is not None
        assert topic_afterwards.locked_by_id == self.admin.id

    def test_unlock_topic(self):
        topic_before = self.create_topic(self.category_id, self.user.id, 1)
        board_topic_service.lock_topic(topic_before, self.admin.id)

        assert topic_before.locked
        assert topic_before.locked_at is not None
        assert topic_before.locked_by_id == self.admin.id

        url = '/board/topics/{}/flags/locked'.format(topic_before.id)
        with self.client(user=self.admin) as client:
            response = client.delete(url)

        assert response.status_code == 204
        topic_afterwards = self.find_topic(topic_before.id)
        assert not topic_afterwards.locked
        assert topic_afterwards.locked_at is None
        assert topic_afterwards.locked_by_id is None
