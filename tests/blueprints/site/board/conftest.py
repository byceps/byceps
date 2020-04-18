"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import pytest

from byceps.services.board import category_command_service
from byceps.services.site import service as site_service
from byceps.services.site import settings_service as site_settings_service

from tests.helpers import (
    assign_permissions_to_user,
    create_brand,
    create_site,
    create_user,
    http_client,
    login_user,
)

from .helpers import create_board, create_category, create_posting, create_topic


@pytest.fixture
def app(party_app_with_db):
    yield party_app_with_db


@pytest.fixture
def site(app, make_email_config):
    email_config = make_email_config()
    site = create_site(email_config_id=email_config.id)
    yield site
    site_service.delete_site(site.id)


@pytest.fixture
def brand(app):
    return create_brand()


@pytest.fixture
def board(app, site, brand):
    board = create_board(brand.id)

    site_settings_service.create_setting(site.id, 'board_id', board.id)

    return board


@pytest.fixture
def category(board):
    category = create_category(board.id, number=1)
    yield category
    category_command_service.delete_category(category.id)


@pytest.fixture
def another_category(board):
    category = create_category(board.id, number=2)
    yield category
    category_command_service.delete_category(category.id)


@pytest.fixture
def topic(category, board_poster):
    return create_topic(category.id, board_poster.id)


@pytest.fixture
def posting(topic, board_poster):
    return create_posting(topic.id, board_poster.id)


@pytest.fixture
def board_poster(app):
    return create_user('BoardPoster')


@pytest.fixture
def moderator(app):
    moderator = create_user('BoardModerator')

    assign_permissions_to_user(
        moderator.id,
        'moderator',
        {
            'board.hide',
            'board_topic.lock',
            'board_topic.move',
            'board_topic.pin',
        },
    )

    login_user(moderator.id)

    return moderator


@pytest.fixture
def moderator_client(app, moderator):
    with http_client(app, user_id=moderator.id) as client:
        yield client
