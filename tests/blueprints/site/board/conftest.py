"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import pytest

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
def site(make_email_config):
    email_config = make_email_config()
    return create_site(email_config_id=email_config.id)


@pytest.fixture
def brand():
    return create_brand()


@pytest.fixture
def board(site, brand):
    board = create_board(brand.id)

    site_settings_service.create_setting(site.id, 'board_id', board.id)

    return board


@pytest.fixture
def category(board):
    return create_category(board.id, number=1)


@pytest.fixture
def another_category(board):
    return create_category(board.id, number=2)


@pytest.fixture
def topic(category, normal_user):
    return create_topic(category.id, normal_user.id)


@pytest.fixture
def posting(topic, normal_user):
    return create_posting(topic.id, normal_user.id)


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
