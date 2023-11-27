"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from flask import Flask
import pytest

from byceps.announce.announce import build_announcement_request
from byceps.events.base import EventUser
from byceps.events.news import NewsItemPublishedEvent
from byceps.services.news.models import NewsChannelID, NewsItemID
from byceps.services.webhooks.models import OutgoingWebhook

from tests.helpers import generate_token, generate_uuid

from .helpers import assert_text, build_webhook


NEWS_CHANNEL_ID = NewsChannelID(generate_token())
NEWS_ITEM_ID = NewsItemID(generate_uuid())


def test_published_news_item_announced_with_url(
    app: Flask, now: datetime, admin: EventUser
) -> None:
    expected_text = (
        '[News] The news "Check this out!" has been published. '
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

    webhook = build_news_webhook()

    actual = build_announcement_request(event, webhook)

    assert_text(actual, expected_text)


def test_published_news_item_announced_without_url(
    app: Flask, now: datetime, admin: EventUser
) -> None:
    expected_text = '[News] The news "Check this out, too!" has been published.'

    event = NewsItemPublishedEvent(
        occurred_at=now,
        initiator=admin,
        item_id=NEWS_ITEM_ID,
        channel_id=NEWS_CHANNEL_ID,
        published_at=now,
        title='Check this out, too!',
        external_url=None,
    )

    webhook = build_news_webhook()

    actual = build_announcement_request(event, webhook)

    assert_text(actual, expected_text)


# helpers


@pytest.fixture(scope='module')
def admin(make_event_user) -> EventUser:
    return make_event_user()


def build_news_webhook() -> OutgoingWebhook:
    return build_webhook(
        event_types={'news-item-published'},
        event_filters={
            'news-item-published': {'channel_id': [str(NEWS_CHANNEL_ID)]}
        },
        text_prefix='[News] ',
        url='https://webhoooks.test/news',
    )
