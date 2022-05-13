"""
:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.services.board import category_command_service

from tests.helpers import log_in_user


@pytest.fixture(scope='package')
def board_admin(make_admin):
    permission_ids = {
        'admin.access',
        'board.create',
        'board.update',
        'board_category.create',
        'board_category.update',
        'board_category.view',
    }
    admin = make_admin(permission_ids)
    log_in_user(admin.id)
    return admin


@pytest.fixture(scope='package')
def board_admin_client(make_client, admin_app, board_admin):
    return make_client(admin_app, user_id=board_admin.id)


@pytest.fixture(scope='module')
def category(board):
    slug = 'beauty-tips'
    title = 'Beauty Tips'
    description = 'Make it pretty!'

    return category_command_service.create_category(
        board.id, slug, title, description
    )
