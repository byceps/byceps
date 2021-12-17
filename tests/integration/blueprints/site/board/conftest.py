"""
:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Iterator, Optional

import pytest

from byceps.services.board.dbmodels.posting import Posting as DbPosting
from byceps.services.board.dbmodels.topic import Topic as DbTopic
from byceps.services.board import (
    category_command_service,
    last_view_service,
    posting_command_service,
    topic_command_service,
    topic_query_service,
)
from byceps.services.board.transfer.models import Board, Category, CategoryID
from byceps.services.user.transfer.models import User

from tests.helpers import log_in_user

from .helpers import create_category, create_posting, create_topic


@pytest.fixture(scope='package')
def category(board: Board) -> Iterator[Category]:
    category = create_category(board.id, number=1)
    yield category
    _delete_category(category.id)


@pytest.fixture(scope='package')
def another_category(board: Board) -> Iterator[Category]:
    category = create_category(board.id, number=2)
    yield category
    _delete_category(category.id)


def _delete_category(category_id: CategoryID) -> None:
    topic_ids = topic_query_service.get_all_topic_ids_in_category(category_id)
    for topic_id in topic_ids:
        last_view_service.delete_last_topic_views(topic_id)
        topic_command_service.delete_topic(topic_id)

    last_view_service.delete_last_category_views(category_id)
    category_command_service.delete_category(category_id)


@pytest.fixture
def topic(category: Category, board_poster: User) -> Iterator[DbTopic]:
    topic = create_topic(category.id, board_poster.id)
    yield topic
    last_view_service.delete_last_topic_views(topic.id)
    topic_command_service.delete_topic(topic.id)


@pytest.fixture
def posting(topic: DbTopic, board_poster: User) -> Iterator[DbPosting]:
    posting = create_posting(topic.id, board_poster.id)
    yield posting
    posting_command_service.delete_posting(posting.id)


@pytest.fixture(scope='package')
def board_poster(make_user) -> User:
    return make_user()


@pytest.fixture(scope='package')
def moderator(make_admin) -> User:
    permission_ids = {
        'board.hide',
        'board_topic.lock',
        'board_topic.move',
        'board_topic.pin',
    }
    moderator = make_admin('BoardModerator', permission_ids)
    log_in_user(moderator.id)
    return moderator


@pytest.fixture(scope='package')
def moderator_client(make_client, site_app, moderator: User):
    return make_client(site_app, user_id=moderator.id)
