# -*- coding: utf-8 -*-

"""
:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime

from byceps.blueprints.board.models.category import Category
from byceps.blueprints.board.models.topic import Topic
from byceps.blueprints.board import service as board_service
from byceps.services.authorization import service as authorization_service

from testfixtures.board import create_category, create_topic
from testfixtures.user import create_user

from tests.base import AbstractAppTestCase


class BoardModerationTestCase(AbstractAppTestCase):

    def setUp(self):
        super(BoardModerationTestCase, self).setUp()

    def test_hide_topic(self):
        self.setup_admin('board_topic.hide')

        user = self.create_user()
        category = self.create_category(1)
        topic_before = self.create_topic(category, user, 1)
        self.db.session.commit()

        self.assertFalse(topic_before.hidden)
        self.assertIsNone(topic_before.hidden_at)
        self.assertIsNone(topic_before.hidden_by)

        url = '/board/topics/{}/flags/hidden'.format(topic_before.id)
        with self.client(user=self.admin) as client:
            response = client.post(url)

        self.assertEqual(response.status_code, 204)
        topic_afterwards = self.find_topic(topic_before.id)
        self.assertTrue(topic_afterwards.hidden)
        self.assertIsNotNone(topic_afterwards.hidden_at)
        self.assertEqual(topic_afterwards.hidden_by, self.admin)

    def test_unhide_topic(self):
        self.setup_admin('board_topic.hide')

        user = self.create_user()
        category = self.create_category(1)
        topic_before = self.create_topic(category, user, 1)
        board_service.hide_topic(topic_before, self.admin)

        self.assertTrue(topic_before.hidden)
        self.assertIsNotNone(topic_before.hidden_at)
        self.assertEqual(topic_before.hidden_by, self.admin)

        url = '/board/topics/{}/flags/hidden'.format(topic_before.id)
        with self.client(user=self.admin) as client:
            response = client.delete(url)

        self.assertEqual(response.status_code, 204)
        topic_afterwards = self.find_topic(topic_before.id)
        self.assertFalse(topic_afterwards.hidden)
        self.assertIsNone(topic_afterwards.hidden_at)
        self.assertIsNone(topic_afterwards.hidden_by)

    def test_lock_topic(self):
        self.setup_admin('board_topic.lock')

        user = self.create_user()
        category = self.create_category(1)
        topic_before = self.create_topic(category, user, 1)

        self.assertFalse(topic_before.locked)
        self.assertIsNone(topic_before.locked_at)
        self.assertIsNone(topic_before.locked_by)

        url = '/board/topics/{}/flags/locked'.format(topic_before.id)
        with self.client(user=self.admin) as client:
            response = client.post(url)

        self.assertEqual(response.status_code, 204)
        topic_afterwards = self.find_topic(topic_before.id)
        self.assertTrue(topic_afterwards.locked)
        self.assertIsNotNone(topic_afterwards.locked_at)
        self.assertEqual(topic_afterwards.locked_by, self.admin)

    def test_unlock_topic(self):
        self.setup_admin('board_topic.lock')

        user = self.create_user()
        category = self.create_category(1)
        topic_before = self.create_topic(category, user, 1)
        board_service.lock_topic(topic_before, self.admin)

        self.assertTrue(topic_before.locked)
        self.assertIsNotNone(topic_before.locked_at)
        self.assertEqual(topic_before.locked_by, self.admin)

        url = '/board/topics/{}/flags/locked'.format(topic_before.id)
        with self.client(user=self.admin) as client:
            response = client.delete(url)

        self.assertEqual(response.status_code, 204)
        topic_afterwards = self.find_topic(topic_before.id)
        self.assertFalse(topic_afterwards.locked)
        self.assertIsNone(topic_afterwards.locked_at)
        self.assertIsNone(topic_afterwards.locked_by)

    def test_pin_topic(self):
        self.setup_admin('board_topic.pin')

        user = self.create_user()
        category = self.create_category(1)
        topic_before = self.create_topic(category, user, 1)

        self.assertFalse(topic_before.pinned)
        self.assertIsNone(topic_before.pinned_at)
        self.assertIsNone(topic_before.pinned_by)

        url = '/board/topics/{}/flags/pinned'.format(topic_before.id)
        with self.client(user=self.admin) as client:
            response = client.post(url)

        self.assertEqual(response.status_code, 204)
        topic_afterwards = self.find_topic(topic_before.id)
        self.assertTrue(topic_afterwards.pinned)
        self.assertIsNotNone(topic_afterwards.pinned_at)
        self.assertEqual(topic_afterwards.pinned_by, self.admin)

    def test_unpin_topic(self):
        self.setup_admin('board_topic.pin')

        user = self.create_user()
        category = self.create_category(1)
        topic_before = self.create_topic(category, user, 1)
        board_service.pin_topic(topic_before, self.admin)

        self.assertTrue(topic_before.pinned)
        self.assertIsNotNone(topic_before.pinned_at)
        self.assertEqual(topic_before.pinned_by, self.admin)

        url = '/board/topics/{}/flags/pinned'.format(topic_before.id)
        with self.client(user=self.admin) as client:
            response = client.delete(url)

        self.assertEqual(response.status_code, 204)
        topic_afterwards = self.find_topic(topic_before.id)
        self.assertFalse(topic_afterwards.pinned)
        self.assertIsNone(topic_afterwards.pinned_at)
        self.assertIsNone(topic_afterwards.pinned_by)

    def test_move_topic(self):
        self.setup_admin('board_topic.move')

        user = self.create_user()
        category1 = self.create_category(1)
        category2 = self.create_category(2)
        topic_before = self.create_topic(category1, user, 1)

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
        number = 1
        screen_name = 'User-{:d}'.format(number)
        email_address = 'user{:03d}@example.com'.format(number)

        user = create_user(number,
                           screen_name=screen_name,
                           email_address=email_address)
        self.db.session.add(user)
        return user

    def setup_admin(self, permission_id):
        permission = authorization_service.create_permission(permission_id,
                                                             permission_id)

        role_id = 'board_moderator'
        role = authorization_service.create_role(role_id, role_id)

        authorization_service.assign_permission_to_role(permission, role)
        authorization_service.assign_role_to_user(role, self.admin)

    def create_category(self, number):
        return create_category(brand=self.brand, number=number)

    def create_topic(self, category, creator, number):
        return create_topic(category, creator, number=number)

    def find_topic(self, id):
        return Topic.query.get(id)
