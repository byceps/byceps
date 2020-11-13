"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.services.board import (
    category_command_service,
    posting_command_service,
    topic_command_service,
    topic_query_service,
)

from tests.helpers import http_client, login_user

from .helpers import create_category, create_posting, create_topic


@pytest.fixture(scope='package')
def category(board):
    category = create_category(board.id, number=1)
    yield category
    _delete_category(category.id)


@pytest.fixture(scope='package')
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


@pytest.fixture(scope='package')
def board_poster(make_user):
    return make_user('BoardPoster')


@pytest.fixture(scope='package')
def moderator(make_admin):
    permission_ids = {
        'board.hide',
        'board_topic.lock',
        'board_topic.move',
        'board_topic.pin',
    }
    moderator = make_admin('BoardModerator', permission_ids)
    login_user(moderator.id)
    yield moderator


@pytest.fixture(scope='package')
def moderator_client(site_app, moderator):
    with http_client(site_app, user_id=moderator.id) as client:
        yield client
