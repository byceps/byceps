# -*- coding: utf-8 -*-

from datetime import datetime

from byceps.blueprints.authorization.models import Permission, Role
from byceps.blueprints.board.authorization import BoardTopicPermission
from byceps.blueprints.board.models import Category, Topic
from byceps.blueprints.user.models import User

from tests import AbstractAppTestCase


class BoardModerationTestCase(AbstractAppTestCase):

    def setUp(self):
        super(BoardModerationTestCase, self).setUp()

    def test_hide_topic(self):
        self.setup_current_user(BoardTopicPermission.hide)

        user = self.create_user(1)
        category = self.create_category(1)
        topic_before = self.create_topic(category, user, 1)
        self.db.session.commit()

        self.assertFalse(topic_before.hidden)
        self.assertIsNone(topic_before.hidden_at)
        self.assertIsNone(topic_before.hidden_by)

        url = '/board/topics/{}/flags/hidden'.format(topic_before.id)
        self.enrich_session_for_user(self.current_user)
        response = self.client.post(url)

        self.assertEqual(response.status_code, 204)
        topic_afterwards = self.find_topic(topic_before.id)
        self.assertTrue(topic_afterwards.hidden)
        self.assertIsNotNone(topic_afterwards.hidden_at)
        self.assertEqual(topic_afterwards.hidden_by, self.current_user)

    def test_unhide_topic(self):
        self.setup_current_user(BoardTopicPermission.hide)

        user = self.create_user(1)
        category = self.create_category(1)
        topic_before = self.create_topic(category, user, 1)
        topic_before.hide(self.current_user)
        self.db.session.commit()

        self.assertTrue(topic_before.hidden)
        self.assertIsNotNone(topic_before.hidden_at)
        self.assertEqual(topic_before.hidden_by, self.current_user)

        url = '/board/topics/{}/flags/hidden'.format(topic_before.id)
        self.enrich_session_for_user(self.current_user)
        response = self.client.delete(url)

        self.assertEqual(response.status_code, 204)
        topic_afterwards = self.find_topic(topic_before.id)
        self.assertFalse(topic_afterwards.hidden)
        self.assertIsNone(topic_afterwards.hidden_at)
        self.assertIsNone(topic_afterwards.hidden_by)

    def test_lock_topic(self):
        self.setup_current_user(BoardTopicPermission.lock)

        user = self.create_user(1)
        category = self.create_category(1)
        topic_before = self.create_topic(category, user, 1)
        self.db.session.commit()

        self.assertFalse(topic_before.locked)
        self.assertIsNone(topic_before.locked_at)
        self.assertIsNone(topic_before.locked_by)

        url = '/board/topics/{}/flags/locked'.format(topic_before.id)
        self.enrich_session_for_user(self.current_user)
        response = self.client.post(url)

        self.assertEqual(response.status_code, 204)
        topic_afterwards = self.find_topic(topic_before.id)
        self.assertTrue(topic_afterwards.locked)
        self.assertIsNotNone(topic_afterwards.locked_at)
        self.assertEqual(topic_afterwards.locked_by, self.current_user)

    def test_unlock_topic(self):
        self.setup_current_user(BoardTopicPermission.lock)

        user = self.create_user(1)
        category = self.create_category(1)
        topic_before = self.create_topic(category, user, 1)
        topic_before.lock(self.current_user)
        self.db.session.commit()

        self.assertTrue(topic_before.locked)
        self.assertIsNotNone(topic_before.locked_at)
        self.assertEqual(topic_before.locked_by, self.current_user)

        url = '/board/topics/{}/flags/locked'.format(topic_before.id)
        self.enrich_session_for_user(self.current_user)
        response = self.client.delete(url)

        self.assertEqual(response.status_code, 204)
        topic_afterwards = self.find_topic(topic_before.id)
        self.assertFalse(topic_afterwards.locked)
        self.assertIsNone(topic_afterwards.locked_at)
        self.assertIsNone(topic_afterwards.locked_by)

    def test_pin_topic(self):
        self.setup_current_user(BoardTopicPermission.pin)

        user = self.create_user(1)
        category = self.create_category(1)
        topic_before = self.create_topic(category, user, 1)
        self.db.session.commit()

        self.assertFalse(topic_before.pinned)
        self.assertIsNone(topic_before.pinned_at)
        self.assertIsNone(topic_before.pinned_by)

        url = '/board/topics/{}/flags/pinned'.format(topic_before.id)
        self.enrich_session_for_user(self.current_user)
        response = self.client.post(url)

        self.assertEqual(response.status_code, 204)
        topic_afterwards = self.find_topic(topic_before.id)
        self.assertTrue(topic_afterwards.pinned)
        self.assertIsNotNone(topic_afterwards.pinned_at)
        self.assertEqual(topic_afterwards.pinned_by, self.current_user)

    def test_unpin_topic(self):
        self.setup_current_user(BoardTopicPermission.pin)

        user = self.create_user(1)
        category = self.create_category(1)
        topic_before = self.create_topic(category, user, 1)
        topic_before.pin(self.current_user)
        self.db.session.commit()

        self.assertTrue(topic_before.pinned)
        self.assertIsNotNone(topic_before.pinned_at)
        self.assertEqual(topic_before.pinned_by, self.current_user)

        url = '/board/topics/{}/flags/pinned'.format(topic_before.id)
        self.enrich_session_for_user(self.current_user)
        response = self.client.delete(url)

        self.assertEqual(response.status_code, 204)
        topic_afterwards = self.find_topic(topic_before.id)
        self.assertFalse(topic_afterwards.pinned)
        self.assertIsNone(topic_afterwards.pinned_at)
        self.assertIsNone(topic_afterwards.pinned_by)

    def test_move_topic(self):
        self.setup_current_user(BoardTopicPermission.move)

        user = self.create_user(1)
        category1 = self.create_category(1)
        category2 = self.create_category(2)
        topic_before = self.create_topic(category1, user, 1)
        self.db.session.commit()

        self.assertEqual(topic_before.category, category1)

        url = '/board/topics/{}/move'.format(topic_before.id)
        form_data = {'category_id': category2.id}
        self.enrich_session_for_user(self.current_user)
        response = self.client.post(url, data=form_data)

        self.assertEqual(response.status_code, 302)
        topic_afterwards = self.find_topic(topic_before.id)
        self.assertEqual(topic_afterwards.category, category2)

    # -------------------------------------------------------------------- #
    # helpers

    def create_user(self, number, *, enabled=True):
        screen_name = 'User-{:d}'.format(number)
        email_address = 'user{:03d}@example.com'.format(number)
        user = User.create(screen_name, email_address, 'le_password')
        user.enabled = enabled
        self.db.session.add(user)
        return user

    def setup_current_user(self, permission=None):
        db_permission = Permission.from_enum_member(permission)
        self.db.session.add(db_permission)

        board_moderator_role = Role(id='board_moderator')
        self.db.session.add(board_moderator_role)

        board_moderator_role.permissions.append(db_permission)

        self.current_user = self.create_user(99, enabled=True)
        self.current_user.roles.add(board_moderator_role)

        self.db.session.commit()

    def create_category(self, number):
        category = Category(
            brand=self.brand,
            position=number,
            slug='category-{}'.format(number),
            title='Kategorie {}'.format(number))
        self.db.session.add(category)
        return category

    def create_topic(self, category, creator, number):
        title = 'Thema {}'.format(number)
        body = 'Inhalt von Thema {}'.format(number)
        topic = Topic.create(category, creator, title, body)
        self.db.session.add(topic)
        return topic

    def find_topic(self, id):
        return Topic.query.get(id)
