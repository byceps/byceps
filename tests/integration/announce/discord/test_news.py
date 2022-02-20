"""
:Copyright: 2006-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import Flask
import pytest

import byceps.announce.connections  # Connect signal handlers.
from byceps.services.brand.transfer.models import Brand
from byceps.services.news import (
    channel_service as news_channel_service,
    service as news_service,
)
from byceps.services.news.transfer.models import (
    BodyFormat,
    Channel,
    ChannelID,
    Item,
)
from byceps.services.webhooks import service as webhook_service
from byceps.signals import news as news_signals

from tests.helpers import generate_token

from .helpers import assert_request, mocked_webhook_receiver


WEBHOOK_URL = 'https://webhoooks.test/news'


def test_published_news_item_announced(
    webhook_settings, admin_app: Flask, item: Item
) -> None:
    expected_content = (
        '[News] Die News "Zieh dir das rein!" wurde veröffentlicht. '
        + 'https://acme.example.com/news/zieh-dir-das-rein'
    )

    event = news_service.publish_item(item.id)

    with mocked_webhook_receiver(WEBHOOK_URL) as mock:
        news_signals.item_published.send(None, event=event)

    assert_request(mock, expected_content)


# helpers


@pytest.fixture
def webhook_settings(channel: Channel) -> None:
    news_channel_ids = [str(channel.id), 'totally-different-id']
    format = 'discord'
    text_prefix = '[News] '
    url = WEBHOOK_URL
    enabled = True

    for news_channel_id in news_channel_ids:
        webhook_service.create_outgoing_webhook(
            # event_types
            {'news-item-published'},
            # event_filters
            {'news-item-published': {'channel_id': [news_channel_id]}},
            format,
            url,
            enabled,
            text_prefix=text_prefix,
        )


@pytest.fixture
def channel(brand: Brand) -> Channel:
    channel_id = ChannelID(generate_token())
    url_prefix = 'https://acme.example.com/news/'

    return news_channel_service.create_channel(brand.id, channel_id, url_prefix)


@pytest.fixture
def item(channel: Channel, make_user) -> Item:
    editor = make_user()
    slug = 'zieh-dir-das-rein'
    title = 'Zieh dir das rein!'
    body = 'any body'
    body_format = BodyFormat.html

    return news_service.create_item(
        channel.id, slug, editor.id, title, body, body_format
    )
