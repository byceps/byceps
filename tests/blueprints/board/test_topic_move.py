"""
:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from .topic_moderation_base import AbstractTopicModerationTest


class TopicMoveTest(AbstractTopicModerationTest):

    def setUp(self):
        super().setUp()

        self.setup_admin_with_permission('board_topic.move')

        self.category_id_1 = self.create_category(1).id
        self.category_id_2 = self.create_category(2).id

    def test_move_topic(self):
        topic_before = self.create_topic(self.category_id_1, self.user.id, 1)

        assert topic_before.category.id == self.category_id_1

        url = '/board/topics/{}/move'.format(topic_before.id)
        form_data = {'category_id': self.category_id_2}
        with self.client(user=self.admin) as client:
            response = client.post(url, data=form_data)

        assert response.status_code == 302
        topic_afterwards = self.find_topic(topic_before.id)
        assert topic_afterwards.category.id == self.category_id_2
