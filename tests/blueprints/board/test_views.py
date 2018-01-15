"""
:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.services.board.models.topic import Topic
from byceps.services.board import topic_service as board_topic_service

from testfixtures.board import create_board, create_category, create_topic

from tests.base import AbstractAppTestCase
from tests.helpers import assign_permissions_to_user


class BoardModerationTestCase(AbstractAppTestCase):

    def setUp(self):
        super().setUp()

        self.admin = self.create_user('Admin')
        self.create_session_token(self.admin.id)

        self.user = self.create_user('User')

        self.create_brand_and_party()

        self.board = self.create_board()

    def test_hide_topic(self):
        self.setup_admin_with_permission('board.hide')

        category = self.create_category(1)
        topic_before = self.create_topic(category.id, self.user.id, 1)
        self.db.session.commit()

        assert not topic_before.hidden
        assert topic_before.hidden_at is None
        assert topic_before.hidden_by_id is None

        url = '/board/topics/{}/flags/hidden'.format(topic_before.id)
        with self.client(user=self.admin) as client:
            response = client.post(url)

        assert response.status_code == 204
        topic_afterwards = self.find_topic(topic_before.id)
        assert topic_afterwards.hidden
        assert topic_afterwards.hidden_at is not None
        assert topic_afterwards.hidden_by_id == self.admin.id

    def test_unhide_topic(self):
        self.setup_admin_with_permission('board.hide')

        category = self.create_category(1)
        topic_before = self.create_topic(category.id, self.user.id, 1)
        board_topic_service.hide_topic(topic_before, self.admin.id)

        assert topic_before.hidden
        assert topic_before.hidden_at is not None
        assert topic_before.hidden_by_id == self.admin.id

        url = '/board/topics/{}/flags/hidden'.format(topic_before.id)
        with self.client(user=self.admin) as client:
            response = client.delete(url)

        assert response.status_code == 204
        topic_afterwards = self.find_topic(topic_before.id)
        assert not topic_afterwards.hidden
        assert topic_afterwards.hidden_at is None
        assert topic_afterwards.hidden_by_id is None

    def test_lock_topic(self):
        self.setup_admin_with_permission('board_topic.lock')

        category = self.create_category(1)
        topic_before = self.create_topic(category.id, self.user.id, 1)

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
        self.setup_admin_with_permission('board_topic.lock')

        category = self.create_category(1)
        topic_before = self.create_topic(category.id, self.user.id, 1)
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

    def test_pin_topic(self):
        self.setup_admin_with_permission('board_topic.pin')

        category = self.create_category(1)
        topic_before = self.create_topic(category.id, self.user.id, 1)

        assert not topic_before.pinned
        assert topic_before.pinned_at is None
        assert topic_before.pinned_by_id is None

        url = '/board/topics/{}/flags/pinned'.format(topic_before.id)
        with self.client(user=self.admin) as client:
            response = client.post(url)

        assert response.status_code == 204
        topic_afterwards = self.find_topic(topic_before.id)
        assert topic_afterwards.pinned
        assert topic_afterwards.pinned_at is not None
        assert topic_afterwards.pinned_by_id == self.admin.id

    def test_unpin_topic(self):
        self.setup_admin_with_permission('board_topic.pin')

        category = self.create_category(1)
        topic_before = self.create_topic(category.id, self.user.id, 1)
        board_topic_service.pin_topic(topic_before, self.admin.id)

        assert topic_before.pinned
        assert topic_before.pinned_at is not None
        assert topic_before.pinned_by_id == self.admin.id

        url = '/board/topics/{}/flags/pinned'.format(topic_before.id)
        with self.client(user=self.admin) as client:
            response = client.delete(url)

        assert response.status_code == 204
        topic_afterwards = self.find_topic(topic_before.id)
        assert not topic_afterwards.pinned
        assert topic_afterwards.pinned_at is None
        assert topic_afterwards.pinned_by_id is None

    def test_move_topic(self):
        self.setup_admin_with_permission('board_topic.move')

        category1 = self.create_category(1)
        category2 = self.create_category(2)
        topic_before = self.create_topic(category1.id, self.user.id, 1)

        assert topic_before.category == category1

        url = '/board/topics/{}/move'.format(topic_before.id)
        form_data = {'category_id': category2.id}
        with self.client(user=self.admin) as client:
            response = client.post(url, data=form_data)

        assert response.status_code == 302
        topic_afterwards = self.find_topic(topic_before.id)
        assert topic_afterwards.category == category2

    # -------------------------------------------------------------------- #
    # helpers

    def setup_admin_with_permission(self, permission_id):
        permission_ids = {'admin.access', permission_id}
        assign_permissions_to_user(self.admin.id, 'admin', permission_ids)

    def create_board(self):
        board_id = self.brand.id
        return create_board(self.brand.id, board_id)

    def create_category(self, number):
        return create_category(self.board.id, number=number)

    def create_topic(self, category_id, creator_id, number):
        return create_topic(category_id, creator_id, number=number)

    def find_topic(self, id):
        return Topic.query.get(id)
