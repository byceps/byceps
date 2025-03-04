"""
:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

import pytest

from byceps.announce.announce import build_announcement_request
from byceps.byceps_app import BycepsApp
from byceps.services.core.events import EventUser
from byceps.services.news.events import NewsItemPublishedEvent
from byceps.services.news.models import NewsChannelID, NewsItemID

from tests.helpers import generate_token, generate_uuid

from .helpers import assert_text


NEWS_CHANNEL_ID = NewsChannelID(generate_token())
NEWS_ITEM_ID = NewsItemID(generate_uuid())


def test_published_news_item_announced_with_url(
    app: BycepsApp, now: datetime, admin: EventUser, webhook_for_irc
) -> None:
    expected_text = (
        'The news "Check this out!" has been published. '
        'https://www.acmecon.test/news/check-this-out'
    )

    event = NewsItemPublishedEvent(
        occurred_at=now,
        initiator=admin,
        item_id=NEWS_ITEM_ID,
        channel_id=NEWS_CHANNEL_ID,
        published_at=now,
        title='Check this out!',
        external_url='https://www.acmecon.test/news/check-this-out',
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


def test_published_news_item_announced_without_url(
    app: BycepsApp, now: datetime, admin: EventUser, webhook_for_irc
) -> None:
    expected_text = 'The news "Check this out, too!" has been published.'

    event = NewsItemPublishedEvent(
        occurred_at=now,
        initiator=admin,
        item_id=NEWS_ITEM_ID,
        channel_id=NEWS_CHANNEL_ID,
        published_at=now,
        title='Check this out, too!',
        external_url=None,
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


# helpers


@pytest.fixture(scope='module')
def admin(make_event_user) -> EventUser:
    return make_event_user(screen_name='Admin')
