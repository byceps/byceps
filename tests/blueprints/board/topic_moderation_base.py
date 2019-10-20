"""
:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.services.board.models.topic import Topic
from byceps.services.site import settings_service as site_settings_service

from testfixtures.board import (
    create_board as _create_board,
    create_category as _create_category,
    create_topic as _create_topic,
)

from tests.base import AbstractAppTestCase
from tests.helpers import (
    assign_permissions_to_user,
    create_brand,
    create_email_config,
    create_site,
    create_user,
    login_user,
)


class AbstractTopicModerationTest(AbstractAppTestCase):

    def setUp(self):
        super().setUp()

        self.admin = create_user('Admin')
        login_user(self.admin.id)

        self.user = create_user('User')

        self.board = setup_board()


# helpers


def setup_admin_with_permission(admin_id, permission_id):
    permission_ids = {'admin.access', permission_id}
    assign_permissions_to_user(admin_id, 'admin', permission_ids)


def setup_board():
    create_email_config()
    site = create_site()

    brand = create_brand()
    board = create_board(brand.id)

    site_settings_service.create_setting(site.id, 'board_id', board.id)

    return board


def create_board(brand_id):
    board_id = brand_id
    return _create_board(brand_id, board_id)


def create_category(board_id, number):
    return _create_category(board_id, number=number)


def create_topic(category_id, creator_id, number):
    return _create_topic(category_id, creator_id, number=number)


def find_topic(topic_id):
    return Topic.query.get(topic_id)
