"""
:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

import pytest

from byceps.announce.announce import build_announcement_request
from byceps.byceps_app import BycepsApp
from byceps.services.board.events import (
    BoardPostingCreatedEvent,
    BoardTopicCreatedEvent,
)
from byceps.services.board.models import (
    BoardCategoryID,
    BoardID,
    PostingID,
    TopicID,
)
from byceps.services.core.events import EventBrand
from byceps.services.user.models import User
from byceps.services.webhooks.models import OutgoingWebhook

from tests.helpers import generate_token, generate_uuid

from .helpers import assert_text, build_webhook


BOARD_ID = BoardID(generate_token())
CATEGORY_1_ID = BoardCategoryID(generate_uuid())
CATEGORY_1_TITLE = 'Category 1'
CATEGORY_2_ID = BoardCategoryID(generate_uuid())
CATEGORY_2_TITLE = 'Category 2'
TOPIC_ID = TopicID(generate_uuid())
POSTING_ID = PostingID(generate_uuid())


def test_announce_topic_created(
    app: BycepsApp, now: datetime, author: User, brand: EventBrand
):
    expected_url = f'https://website.test/board/topics/{TOPIC_ID}'
    expected_text = (
        '[Forum] RocketRandy has created topic '
        '"Cannot connect to the party network :(": '
        f'<{expected_url}>'
    )

    event = BoardTopicCreatedEvent(
        occurred_at=now,
        initiator=author,
        brand=brand,
        board_id=BOARD_ID,
        topic_id=TOPIC_ID,
        topic_creator=author,
        topic_title='Cannot connect to the party network :(',
        url=expected_url,
    )

    webhook = build_board_webhook(BOARD_ID)

    actual = build_announcement_request(event, webhook)

    assert_text(actual, expected_text)


def test_announce_posting_created(
    app: BycepsApp, now: datetime, author: User, brand: EventBrand
):
    expected_url = f'https://website.test/board/postings/{POSTING_ID}'
    expected_text = (
        '[Forum] RocketRandy replied in topic '
        '"Cannot connect to the party network :(": '
        f'<{expected_url}>'
    )

    event = BoardPostingCreatedEvent(
        occurred_at=now,
        initiator=author,
        brand=brand,
        board_id=BOARD_ID,
        posting_id=POSTING_ID,
        posting_creator=author,
        topic_id=TOPIC_ID,
        topic_title='Cannot connect to the party network :(',
        topic_muted=False,
        url=expected_url,
    )

    webhook = build_board_webhook(BOARD_ID)

    actual = build_announcement_request(event, webhook)

    assert_text(actual, expected_text)


# helpers


@pytest.fixture(scope='module')
def author(make_user) -> User:
    return make_user(screen_name='RocketRandy')


@pytest.fixture(scope='module')
def brand(make_event_brand) -> EventBrand:
    return make_event_brand()


def build_board_webhook(board_id: BoardID) -> OutgoingWebhook:
    return build_webhook(
        event_types={
            'board-posting-created',
            'board-topic-created',
        },
        event_filters={
            'board-posting-created': {'board_id': [str(board_id)]},
            'board-topic-created': {'board_id': [str(board_id)]},
        },
        text_prefix='[Forum] ',
        url='https://webhoooks.test/board',
    )
