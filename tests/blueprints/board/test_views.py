"""
:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.services.board.models.topic import Topic
from byceps.services.board import topic_service as board_topic_service

from testfixtures.board import create_category, create_topic
from testfixtures.user import create_user

from tests.base import AbstractAppTestCase
from tests.helpers import assign_permissions_to_user


class BoardModerationTestCase(AbstractAppTestCase):

    def setUp(self):
        super().setUp()

        self.user = self.create_user()

    def test_hide_topic(self):
        self.setup_admin('board_topic.hide')

        category = self.create_category(1)
        topic_before = self.create_topic(category, self.user.id, 1)
        self.db.session.commit()

        self.assertFalse(topic_before.hidden)
        self.assertIsNone(topic_before.hidden_at)
        self.assertIsNone(topic_before.hidden_by_id)

        url = '/board/topics/{}/flags/hidden'.format(topic_before.id)
        with self.client(user=self.admin) as client:
            response = client.post(url)

        self.assertEqual(response.status_code, 204)
        topic_afterwards = self.find_topic(topic_before.id)
        self.assertTrue(topic_afterwards.hidden)
        self.assertIsNotNone(topic_afterwards.hidden_at)
        self.assertEqual(topic_afterwards.hidden_by_id, self.admin.id)

    def test_unhide_topic(self):
        self.setup_admin('board_topic.hide')

        category = self.create_category(1)
        topic_before = self.create_topic(category, self.user.id, 1)
        board_topic_service.hide_topic(topic_before, self.admin.id)

        self.assertTrue(topic_before.hidden)
        self.assertIsNotNone(topic_before.hidden_at)
        self.assertEqual(topic_before.hidden_by_id, self.admin.id)

        url = '/board/topics/{}/flags/hidden'.format(topic_before.id)
        with self.client(user=self.admin) as client:
            response = client.delete(url)

        self.assertEqual(response.status_code, 204)
        topic_afterwards = self.find_topic(topic_before.id)
        self.assertFalse(topic_afterwards.hidden)
        self.assertIsNone(topic_afterwards.hidden_at)
        self.assertIsNone(topic_afterwards.hidden_by_id)

    def test_lock_topic(self):
        self.setup_admin('board_topic.lock')

        category = self.create_category(1)
        topic_before = self.create_topic(category, self.user.id, 1)

        self.assertFalse(topic_before.locked)
        self.assertIsNone(topic_before.locked_at)
        self.assertIsNone(topic_before.locked_by_id)

        url = '/board/topics/{}/flags/locked'.format(topic_before.id)
        with self.client(user=self.admin) as client:
            response = client.post(url)

        self.assertEqual(response.status_code, 204)
        topic_afterwards = self.find_topic(topic_before.id)
        self.assertTrue(topic_afterwards.locked)
        self.assertIsNotNone(topic_afterwards.locked_at)
        self.assertEqual(topic_afterwards.locked_by_id, self.admin.id)

    def test_unlock_topic(self):
        self.setup_admin('board_topic.lock')

        category = self.create_category(1)
        topic_before = self.create_topic(category, self.user.id, 1)
        board_topic_service.lock_topic(topic_before, self.admin.id)

        self.assertTrue(topic_before.locked)
        self.assertIsNotNone(topic_before.locked_at)
        self.assertEqual(topic_before.locked_by_id, self.admin.id)

        url = '/board/topics/{}/flags/locked'.format(topic_before.id)
        with self.client(user=self.admin) as client:
            response = client.delete(url)

        self.assertEqual(response.status_code, 204)
        topic_afterwards = self.find_topic(topic_before.id)
        self.assertFalse(topic_afterwards.locked)
        self.assertIsNone(topic_afterwards.locked_at)
        self.assertIsNone(topic_afterwards.locked_by_id)

    def test_pin_topic(self):
        self.setup_admin('board_topic.pin')

        category = self.create_category(1)
        topic_before = self.create_topic(category, self.user.id, 1)

        self.assertFalse(topic_before.pinned)
        self.assertIsNone(topic_before.pinned_at)
        self.assertIsNone(topic_before.pinned_by_id)

        url = '/board/topics/{}/flags/pinned'.format(topic_before.id)
        with self.client(user=self.admin) as client:
            response = client.post(url)

        self.assertEqual(response.status_code, 204)
        topic_afterwards = self.find_topic(topic_before.id)
        self.assertTrue(topic_afterwards.pinned)
        self.assertIsNotNone(topic_afterwards.pinned_at)
        self.assertEqual(topic_afterwards.pinned_by_id, self.admin.id)

    def test_unpin_topic(self):
        self.setup_admin('board_topic.pin')

        category = self.create_category(1)
        topic_before = self.create_topic(category, self.user.id, 1)
        board_topic_service.pin_topic(topic_before, self.admin.id)

        self.assertTrue(topic_before.pinned)
        self.assertIsNotNone(topic_before.pinned_at)
        self.assertEqual(topic_before.pinned_by_id, self.admin.id)

        url = '/board/topics/{}/flags/pinned'.format(topic_before.id)
        with self.client(user=self.admin) as client:
            response = client.delete(url)

        self.assertEqual(response.status_code, 204)
        topic_afterwards = self.find_topic(topic_before.id)
        self.assertFalse(topic_afterwards.pinned)
        self.assertIsNone(topic_afterwards.pinned_at)
        self.assertIsNone(topic_afterwards.pinned_by_id)

    def test_move_topic(self):
        self.setup_admin('board_topic.move')

        category1 = self.create_category(1)
        category2 = self.create_category(2)
        topic_before = self.create_topic(category1, self.user.id, 1)

        self.assertEqual(topic_before.category, category1)

        url = '/board/topics/{}/move'.format(topic_before.id)
        form_data = {'category_id': category2.id}
        with self.client(user=self.admin) as client:
            response = client.post(url, data=form_data)

        self.assertEqual(response.status_code, 302)
        topic_afterwards = self.find_topic(topic_before.id)
        self.assertEqual(topic_afterwards.category, category2)

    # -------------------------------------------------------------------- #
    # helpers

    def create_user(self):
        user = create_user()
        self.db.session.add(user)
        return user

    def setup_admin(self, permission_id):
        permission_ids = {'admin.access', permission_id}
        assign_permissions_to_user(self.admin.id, 'admin', permission_ids)

    def create_category(self, number):
        return create_category(brand=self.brand, number=number)

    def create_topic(self, category, creator_id, number):
        return create_topic(category, creator_id, number=number)

    def find_topic(self, id):
        return Topic.query.get(id)
