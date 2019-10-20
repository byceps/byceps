"""
:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import pytest

from byceps.services.site import settings_service as site_settings_service


from ...helpers import (
    assign_permissions_to_user,
    create_brand,
    create_email_config,
    create_site,
    login_user,
)

from .helpers import create_board, create_category, create_posting, create_topic


@pytest.fixture
def board():
    create_email_config()
    site = create_site()

    brand = create_brand()
    board = create_board(brand.id)

    site_settings_service.create_setting(site.id, 'board_id', board.id)

    return board


@pytest.fixture
def category(board):
    return create_category(board.id, 1)


@pytest.fixture
def topic(category, normal_user):
    return create_topic(category.id, normal_user.id, 1)


@pytest.fixture
def posting(topic, normal_user):
    return create_posting(topic.id, normal_user.id, 1)


@pytest.fixture
def make_moderator(admin_user):
    def _wrapper(permission_id):
        setup_admin_with_permission(admin_user.id, permission_id)
        login_user(admin_user.id)
        return admin_user

    return _wrapper


def setup_admin_with_permission(admin_id, permission_id):
    permission_ids = {'admin.access', permission_id}
    assign_permissions_to_user(admin_id, 'admin', permission_ids)
