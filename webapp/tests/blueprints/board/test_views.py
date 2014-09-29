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

        assert topic_before.hidden == False
        assert topic_before.hidden_at is None
        assert topic_before.hidden_by is None

        url = '/board/topics/{}/flags/hidden'.format(topic_before.id)
        with self.client.session_transaction() as session:
            session['user_id'] = str(self.current_user.id)
        response = self.client.post(url)

        assert response.status_code == 204
        topic_afterwards = self.find_topic(topic_before.id)
        assert topic_afterwards.hidden == True
        assert topic_afterwards.hidden_at is not None
        assert topic_afterwards.hidden_by is not None

    def test_unhide_topic(self):
        self.setup_current_user(BoardTopicPermission.hide)

        user = self.create_user(1)
        category = self.create_category(1)
        topic_before = self.create_topic(category, user, 1)
        topic_before.hide(self.current_user)
        self.db.session.commit()

        assert topic_before.hidden == True
        assert topic_before.hidden_at is not None
        assert topic_before.hidden_by is not None

        url = '/board/topics/{}/flags/hidden'.format(topic_before.id)
        with self.client.session_transaction() as session:
            session['user_id'] = str(self.current_user.id)
        response = self.client.delete(url)

        assert response.status_code == 204
        topic_afterwards = self.find_topic(topic_before.id)
        assert topic_afterwards.hidden == False
        assert topic_afterwards.hidden_at is None
        assert topic_afterwards.hidden_by is None

    def test_lock_topic(self):
        self.setup_current_user(BoardTopicPermission.lock)

        user = self.create_user(1)
        category = self.create_category(1)
        topic_before = self.create_topic(category, user, 1)
        self.db.session.commit()

        assert topic_before.locked == False
        assert topic_before.locked_at is None
        assert topic_before.locked_by is None

        url = '/board/topics/{}/flags/locked'.format(topic_before.id)
        with self.client.session_transaction() as session:
            session['user_id'] = str(self.current_user.id)
        response = self.client.post(url)

        assert response.status_code == 204
        topic_afterwards = self.find_topic(topic_before.id)
        assert topic_afterwards.locked == True
        assert topic_afterwards.locked_at is not None
        assert topic_afterwards.locked_by is not None

    def test_unlock_topic(self):
        self.setup_current_user(BoardTopicPermission.lock)

        user = self.create_user(1)
        category = self.create_category(1)
        topic_before = self.create_topic(category, user, 1)
        topic_before.lock(self.current_user)
        self.db.session.commit()

        assert topic_before.locked == True
        assert topic_before.locked_at is not None
        assert topic_before.locked_by is not None

        url = '/board/topics/{}/flags/locked'.format(topic_before.id)
        with self.client.session_transaction() as session:
            session['user_id'] = str(self.current_user.id)
        response = self.client.delete(url)

        assert response.status_code == 204
        topic_afterwards = self.find_topic(topic_before.id)
        assert topic_afterwards.locked == False
        assert topic_afterwards.locked_at is None
        assert topic_afterwards.locked_by is None

    def test_pin_topic(self):
        self.setup_current_user(BoardTopicPermission.pin)

        user = self.create_user(1)
        category = self.create_category(1)
        topic_before = self.create_topic(category, user, 1)
        self.db.session.commit()

        assert topic_before.pinned == False
        assert topic_before.pinned_at is None
        assert topic_before.pinned_by is None

        url = '/board/topics/{}/flags/pinned'.format(topic_before.id)
        with self.client.session_transaction() as session:
            session['user_id'] = str(self.current_user.id)
        response = self.client.post(url)

        assert response.status_code == 204
        topic_afterwards = self.find_topic(topic_before.id)
        assert topic_afterwards.pinned == True
        assert topic_afterwards.pinned_at is not None
        assert topic_afterwards.pinned_by is not None

    def test_unpin_topic(self):
        self.setup_current_user(BoardTopicPermission.pin)

        user = self.create_user(1)
        category = self.create_category(1)
        topic_before = self.create_topic(category, user, 1)
        topic_before.pin(self.current_user)
        self.db.session.commit()

        assert topic_before.pinned == True
        assert topic_before.pinned_at is not None
        assert topic_before.pinned_by is not None

        url = '/board/topics/{}/flags/pinned'.format(topic_before.id)
        with self.client.session_transaction() as session:
            session['user_id'] = str(self.current_user.id)
        response = self.client.delete(url)

        assert response.status_code == 204
        topic_afterwards = self.find_topic(topic_before.id)
        assert topic_afterwards.pinned == False
        assert topic_afterwards.pinned_at is None
        assert topic_afterwards.pinned_by is None

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
