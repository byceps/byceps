"""
:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Optional

import pytest

from byceps.services.board.dbmodels.posting import Posting as DbPosting
from byceps.services.board.dbmodels.topic import Topic as DbTopic
from byceps.services.board.transfer.models import Board, Category
from byceps.services.user.transfer.models import User

from tests.helpers import log_in_user

from .helpers import create_category, create_posting, create_topic


@pytest.fixture(scope='package')
def category(board: Board) -> Category:
    return create_category(board.id, number=1)


@pytest.fixture(scope='package')
def another_category(board: Board) -> Category:
    return create_category(board.id, number=2)


@pytest.fixture
def topic(category: Category, board_poster: User) -> DbTopic:
    return create_topic(category.id, board_poster.id)


@pytest.fixture
def posting(topic: DbTopic, board_poster: User) -> DbPosting:
    return create_posting(topic.id, board_poster.id)


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
    moderator = make_admin(permission_ids)
    log_in_user(moderator.id)
    return moderator


@pytest.fixture(scope='package')
def moderator_client(make_client, site_app, moderator: User):
    return make_client(site_app, user_id=moderator.id)
