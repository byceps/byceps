"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import pytest

from byceps.services.board import category_command_service

from tests.helpers import login_user


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
    admin = make_admin('BoardAdmin', permission_ids)
    login_user(admin.id)
    return admin


@pytest.fixture(scope='module')
def category(board):
    slug = 'beauty-tips'
    title = 'Beauty Tips'
    description = 'Make it pretty!'

    category = category_command_service.create_category(
        board.id, slug, title, description
    )

    yield category

    category_command_service.delete_category(category.id)
