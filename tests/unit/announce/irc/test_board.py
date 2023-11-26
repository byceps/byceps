"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from flask import Flask
import pytest

from byceps.announce.announce import build_announcement_request
from byceps.events.base import EventBrand, EventUser
from byceps.events.board import (
    BoardPostingCreatedEvent,
    BoardPostingHiddenEvent,
    BoardPostingUnhiddenEvent,
    BoardTopicCreatedEvent,
    BoardTopicHiddenEvent,
    BoardTopicLockedEvent,
    BoardTopicMovedEvent,
    BoardTopicPinnedEvent,
    BoardTopicUnhiddenEvent,
    BoardTopicUnlockedEvent,
    BoardTopicUnpinnedEvent,
)
from byceps.services.board.models import (
    BoardCategoryID,
    BoardID,
    PostingID,
    TopicID,
)
from byceps.services.brand.models import BrandID
from byceps.services.user.models.user import User

from tests.helpers import generate_token, generate_uuid

from .helpers import assert_text


BRAND_ID = BrandID('acmecon')
BRAND_TITLE = 'ACME Entertainment Convention'
BOARD_ID = BoardID(generate_token())
CATEGORY_1_ID = BoardCategoryID(generate_uuid())
CATEGORY_1_TITLE = 'Category 1'
CATEGORY_2_ID = BoardCategoryID(generate_uuid())
CATEGORY_2_TITLE = 'Category 2'
TOPIC_ID = TopicID(generate_uuid())
POSTING_ID = PostingID(generate_uuid())


def test_announce_topic_created(
    app: Flask, now: datetime, author: User, webhook_for_irc
):
    expected_link = f'http://example.com/board/topics/{TOPIC_ID}'
    expected_text = (
        'TheShadow999 has created topic "Brötchen zum Frühstück" '
        f'in "ACME Entertainment Convention" board: {expected_link}'
    )

    event = BoardTopicCreatedEvent(
        occurred_at=now,
        initiator=EventUser.from_user(author),
        brand=EventBrand(BRAND_ID, BRAND_TITLE),
        board_id=BOARD_ID,
        topic_id=TOPIC_ID,
        topic_creator=EventUser.from_user(author),
        topic_title='Brötchen zum Frühstück',
        url=expected_link,
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


def test_announce_topic_hidden(
    app: Flask, now: datetime, author: User, moderator: User, webhook_for_irc
):
    expected_link = f'http://example.com/board/topics/{TOPIC_ID}'
    expected_text = (
        'TheModerator has hidden topic "Brötchen zum Frühstück" '
        'by TheShadow999 '
        f'in "ACME Entertainment Convention" board: {expected_link}'
    )

    event = BoardTopicHiddenEvent(
        occurred_at=now,
        initiator=EventUser.from_user(moderator),
        brand=EventBrand(BRAND_ID, BRAND_TITLE),
        board_id=BOARD_ID,
        topic_id=TOPIC_ID,
        topic_creator=EventUser.from_user(author),
        topic_title='Brötchen zum Frühstück',
        moderator=EventUser.from_user(moderator),
        url=expected_link,
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


def test_announce_topic_unhidden(
    app: Flask, now: datetime, author: User, moderator: User, webhook_for_irc
):
    expected_link = f'http://example.com/board/topics/{TOPIC_ID}'
    expected_text = (
        'TheModerator has unhidden topic "Brötchen zum Frühstück" '
        'by TheShadow999 '
        f'in "ACME Entertainment Convention" board: {expected_link}'
    )

    event = BoardTopicUnhiddenEvent(
        occurred_at=now,
        initiator=EventUser.from_user(moderator),
        brand=EventBrand(BRAND_ID, BRAND_TITLE),
        board_id=BOARD_ID,
        topic_id=TOPIC_ID,
        topic_creator=EventUser.from_user(author),
        topic_title='Brötchen zum Frühstück',
        moderator=EventUser.from_user(moderator),
        url=expected_link,
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


def test_announce_topic_locked(
    app: Flask, now: datetime, author: User, moderator: User, webhook_for_irc
):
    expected_link = f'http://example.com/board/topics/{TOPIC_ID}'
    expected_text = (
        'TheModerator has closed topic "Brötchen zum Frühstück" '
        'by TheShadow999 '
        f'in "ACME Entertainment Convention" board: {expected_link}'
    )

    event = BoardTopicLockedEvent(
        occurred_at=now,
        initiator=EventUser.from_user(moderator),
        brand=EventBrand(BRAND_ID, BRAND_TITLE),
        board_id=BOARD_ID,
        topic_id=TOPIC_ID,
        topic_creator=EventUser.from_user(author),
        topic_title='Brötchen zum Frühstück',
        moderator=EventUser.from_user(moderator),
        url=expected_link,
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


def test_announce_topic_unlocked(
    app: Flask, now: datetime, author: User, moderator: User, webhook_for_irc
):
    expected_link = f'http://example.com/board/topics/{TOPIC_ID}'
    expected_text = (
        'TheModerator has reopened topic "Brötchen zum Frühstück" '
        'by TheShadow999 '
        f'in "ACME Entertainment Convention" board: {expected_link}'
    )

    event = BoardTopicUnlockedEvent(
        occurred_at=now,
        initiator=EventUser.from_user(moderator),
        brand=EventBrand(BRAND_ID, BRAND_TITLE),
        board_id=BOARD_ID,
        topic_id=TOPIC_ID,
        topic_creator=EventUser.from_user(author),
        topic_title='Brötchen zum Frühstück',
        moderator=EventUser.from_user(moderator),
        url=expected_link,
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


def test_announce_topic_pinned(
    app: Flask, now: datetime, author: User, moderator: User, webhook_for_irc
):
    expected_link = f'http://example.com/board/topics/{TOPIC_ID}'
    expected_text = (
        'TheModerator has pinned topic "Brötchen zum Frühstück" '
        'by TheShadow999 '
        f'in "ACME Entertainment Convention" board: {expected_link}'
    )

    event = BoardTopicPinnedEvent(
        occurred_at=now,
        initiator=EventUser.from_user(moderator),
        brand=EventBrand(BRAND_ID, BRAND_TITLE),
        board_id=BOARD_ID,
        topic_id=TOPIC_ID,
        topic_creator=EventUser.from_user(author),
        topic_title='Brötchen zum Frühstück',
        moderator=EventUser.from_user(moderator),
        url=expected_link,
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


def test_announce_topic_unpinned(
    app: Flask, now: datetime, author: User, moderator: User, webhook_for_irc
):
    expected_link = f'http://example.com/board/topics/{TOPIC_ID}'
    expected_text = (
        'TheModerator has unpinned topic "Brötchen zum Frühstück" '
        'by TheShadow999 '
        f'in "ACME Entertainment Convention" board: {expected_link}'
    )

    event = BoardTopicUnpinnedEvent(
        occurred_at=now,
        initiator=EventUser.from_user(moderator),
        brand=EventBrand(BRAND_ID, BRAND_TITLE),
        board_id=BOARD_ID,
        topic_id=TOPIC_ID,
        topic_creator=EventUser.from_user(author),
        topic_title='Brötchen zum Frühstück',
        moderator=EventUser.from_user(moderator),
        url=expected_link,
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


def test_announce_topic_moved(
    app: Flask, now: datetime, author: User, moderator: User, webhook_for_irc
):
    expected_link = f'http://example.com/board/topics/{TOPIC_ID}'
    expected_text = (
        'TheModerator has moved topic "Brötchen zum Frühstück" '
        'by TheShadow999 '
        'from "Category 1" to "Category 2" '
        f'in "ACME Entertainment Convention" board: {expected_link}'
    )

    event = BoardTopicMovedEvent(
        occurred_at=now,
        initiator=EventUser.from_user(moderator),
        brand=EventBrand(BRAND_ID, BRAND_TITLE),
        board_id=BOARD_ID,
        topic_id=TOPIC_ID,
        topic_creator=EventUser.from_user(author),
        topic_title='Brötchen zum Frühstück',
        old_category_id=CATEGORY_1_ID,
        old_category_title=CATEGORY_1_TITLE,
        new_category_id=CATEGORY_2_ID,
        new_category_title=CATEGORY_2_TITLE,
        moderator=EventUser.from_user(moderator),
        url=expected_link,
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


def test_announce_posting_created(
    app: Flask, now: datetime, author: User, webhook_for_irc
):
    expected_link = f'http://example.com/board/postings/{POSTING_ID}'
    expected_text = (
        'TheShadow999 replied in topic "Brötchen zum Frühstück" '
        f'in "ACME Entertainment Convention" board: {expected_link}'
    )

    event = BoardPostingCreatedEvent(
        occurred_at=now,
        initiator=EventUser.from_user(author),
        brand=EventBrand(BRAND_ID, BRAND_TITLE),
        board_id=BOARD_ID,
        posting_id=POSTING_ID,
        posting_creator=EventUser.from_user(author),
        topic_id=TOPIC_ID,
        topic_title='Brötchen zum Frühstück',
        topic_muted=False,
        url=expected_link,
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


def test_announce_posting_created_on_muted_topic(
    app: Flask, now: datetime, author: User, webhook_for_irc
):
    link = f'http://example.com/board/postings/{POSTING_ID}'

    event = BoardPostingCreatedEvent(
        occurred_at=now,
        initiator=EventUser.from_user(author),
        brand=EventBrand(BRAND_ID, BRAND_TITLE),
        board_id=BOARD_ID,
        posting_id=POSTING_ID,
        posting_creator=EventUser.from_user(author),
        topic_id=TOPIC_ID,
        topic_title='Brötchen zum Frühstück',
        topic_muted=True,
        url=link,
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert actual is None


def test_announce_posting_hidden(
    app: Flask, now: datetime, author: User, moderator: User, webhook_for_irc
):
    expected_link = f'http://example.com/board/postings/{POSTING_ID}'
    expected_text = (
        'TheModerator has hidden a reply by TheShadow999 in topic '
        '"Brötchen zum Frühstück" '
        f'in "ACME Entertainment Convention" board: {expected_link}'
    )

    event = BoardPostingHiddenEvent(
        occurred_at=now,
        initiator=EventUser.from_user(moderator),
        brand=EventBrand(BRAND_ID, BRAND_TITLE),
        board_id=BOARD_ID,
        posting_id=POSTING_ID,
        posting_creator=EventUser.from_user(author),
        topic_id=TOPIC_ID,
        topic_title='Brötchen zum Frühstück',
        moderator=EventUser.from_user(moderator),
        url=expected_link,
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


def test_announce_posting_unhidden(
    app: Flask, now: datetime, author: User, moderator: User, webhook_for_irc
):
    expected_link = f'http://example.com/board/postings/{POSTING_ID}'
    expected_text = (
        'TheModerator has unhidden a reply by TheShadow999 in topic '
        '"Brötchen zum Frühstück" '
        f'in "ACME Entertainment Convention" board: {expected_link}'
    )

    event = BoardPostingUnhiddenEvent(
        occurred_at=now,
        initiator=EventUser.from_user(moderator),
        brand=EventBrand(BRAND_ID, BRAND_TITLE),
        board_id=BOARD_ID,
        posting_id=POSTING_ID,
        posting_creator=EventUser.from_user(author),
        topic_id=TOPIC_ID,
        topic_title='Brötchen zum Frühstück',
        moderator=EventUser.from_user(moderator),
        url=expected_link,
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


# helpers


@pytest.fixture(scope='module')
def author(make_user) -> User:
    return make_user(screen_name='TheShadow999')


@pytest.fixture(scope='module')
def moderator(make_user) -> User:
    return make_user(screen_name='TheModerator')
