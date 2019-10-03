"""
:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from tests.helpers import http_client

from .topic_moderation_base import (
    AbstractTopicModerationTest,
    create_category,
    create_topic,
    find_topic,
    setup_admin_with_permission,
)


class TopicMoveTest(AbstractTopicModerationTest):

    def setUp(self):
        super().setUp()

        setup_admin_with_permission(self.admin.id, 'board_topic.move')

        self.category_id_1 = create_category(self.board.id, 1).id
        self.category_id_2 = create_category(self.board.id, 2).id

    def test_move_topic(self):
        topic_before = create_topic(self.category_id_1, self.user.id, 1)

        assert topic_before.category.id == self.category_id_1

        url = '/board/topics/{}/move'.format(topic_before.id)
        form_data = {'category_id': self.category_id_2}
        with http_client(self.app, user_id=self.admin.id) as client:
            response = client.post(url, data=form_data)

        assert response.status_code == 302
        topic_afterwards = find_topic(topic_before.id)
        assert topic_afterwards.category.id == self.category_id_2
