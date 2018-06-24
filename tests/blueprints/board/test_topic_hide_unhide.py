"""
:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.services.board import topic_service as board_topic_service

from .topic_moderation_base import AbstractTopicModerationTest


class TopicHideTest(AbstractTopicModerationTest):

    def setUp(self):
        super().setUp()

        self.setup_admin_with_permission('board.hide')

        self.category_id = self.create_category(1).id

    def test_hide_topic(self):
        topic_before = self.create_topic(self.category_id, self.user.id, 1)
        self.db.session.commit()

        assert_topic_is_not_hidden(topic_before)

        url = '/board/topics/{}/flags/hidden'.format(topic_before.id)
        with self.client(user=self.admin) as client:
            response = client.post(url)

        assert response.status_code == 204
        topic_afterwards = self.find_topic(topic_before.id)
        assert_topic_is_hidden(topic_afterwards, self.admin.id)

    def test_unhide_topic(self):
        topic_before = self.create_topic(self.category_id, self.user.id, 1)
        board_topic_service.hide_topic(topic_before, self.admin.id)

        assert_topic_is_hidden(topic_before, self.admin.id)

        url = '/board/topics/{}/flags/hidden'.format(topic_before.id)
        with self.client(user=self.admin) as client:
            response = client.delete(url)

        assert response.status_code == 204
        topic_afterwards = self.find_topic(topic_before.id)
        assert_topic_is_not_hidden(topic_afterwards)


def assert_topic_is_hidden(topic, moderator_id):
    assert topic.hidden
    assert topic.hidden_at is not None
    assert topic.hidden_by_id == moderator_id


def assert_topic_is_not_hidden(topic):
    assert not topic.hidden
    assert topic.hidden_at is None
    assert topic.hidden_by_id is None
