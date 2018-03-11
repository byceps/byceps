"""
:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.services.board.models.topic import Topic

from testfixtures.board import create_board, create_category, create_topic

from tests.base import AbstractAppTestCase
from tests.helpers import assign_permissions_to_user


class AbstractTopicModerationTest(AbstractAppTestCase):

    def setUp(self):
        super().setUp()

        self.admin = self.create_user('Admin')
        self.create_session_token(self.admin.id)

        self.user = self.create_user('User')

        self.create_brand_and_party()

        self.board = self.create_board()

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
