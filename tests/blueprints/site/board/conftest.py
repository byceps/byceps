"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import pytest

from byceps.services.authorization import service as authorization_service
from byceps.services.board import (
    board_service,
    category_command_service,
    posting_command_service,
    topic_command_service,
    topic_query_service,
)
from byceps.services.brand import service as brand_service
from byceps.services.site import service as site_service
from byceps.services.site import settings_service as site_settings_service

from tests.helpers import (
    create_brand,
    create_permissions,
    create_role_with_permissions_assigned,
    create_site,
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
    brand = create_brand()
    yield brand
    brand_service.delete_brand(brand.id)


@pytest.fixture
def board(site, brand):
    board = create_board(brand.id)

    site_settings_service.create_setting(site.id, 'board_id', board.id)

    yield board

    board_service.delete_board(board.id)


@pytest.fixture
def category(board):
    category = create_category(board.id, number=1)
    yield category
    _delete_category(category.id)


@pytest.fixture
def another_category(board):
    category = create_category(board.id, number=2)
    yield category
    _delete_category(category.id)


def _delete_category(category_id):
    topic_ids = topic_query_service.get_all_topic_ids_in_category(category_id)
    for topic_id in topic_ids:
        topic_command_service.delete_topic(topic_id)

    category_command_service.delete_category(category_id)


@pytest.fixture
def topic(category, board_poster):
    topic = create_topic(category.id, board_poster.id)
    yield topic
    topic_command_service.delete_topic(topic.id)


@pytest.fixture
def posting(topic, board_poster):
    posting = create_posting(topic.id, board_poster.id)
    yield posting
    posting_command_service.delete_posting(posting.id)


@pytest.fixture
def board_poster(make_user):
    yield from make_user('BoardPoster')


@pytest.fixture
def _moderator(make_user):
    yield from make_user('BoardModerator')


@pytest.fixture
def moderator(_moderator):
    moderator = _moderator

    permission_ids = {
        'board.hide',
        'board_topic.lock',
        'board_topic.move',
        'board_topic.pin',
    }
    role_id = 'moderator'
    create_permissions(permission_ids)
    create_role_with_permissions_assigned(role_id, permission_ids)
    authorization_service.assign_role_to_user(role_id, moderator.id)

    login_user(moderator.id)

    return moderator


@pytest.fixture
def moderator_client(app, moderator):
    with http_client(app, user_id=moderator.id) as client:
        yield client
