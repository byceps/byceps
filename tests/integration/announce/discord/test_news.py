"""
:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

import byceps.announce.connections  # Connect signal handlers.
from byceps.services.news import (
    channel_service as news_channel_service,
    service as news_service,
)
from byceps.services.webhooks import service as webhook_service
from byceps.signals import news as news_signals

from .helpers import assert_request, mocked_webhook_receiver


WEBHOOK_URL = 'https://webhoooks.test/news'


def test_published_news_item_announced(webhook_settings, admin_app, item):
    expected_content = (
        '[News] Die News "Zieh dir das rein!" wurde veröffentlicht. '
        + 'https://acme.example.com/news/zieh-dir-das-rein'
    )

    event = news_service.publish_item(item.id)

    with mocked_webhook_receiver(WEBHOOK_URL) as mock:
        news_signals.item_published.send(None, event=event)

    assert_request(mock, expected_content)


# helpers


@pytest.fixture(scope='module')
def webhook_settings(channel):
    news_channel_ids = [str(channel.id), 'totally-different-id']
    format = 'discord'
    text_prefix = '[News] '
    url = WEBHOOK_URL
    enabled = True

    webhooks = [
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
        for news_channel_id in news_channel_ids
    ]

    yield

    for webhook in webhooks:
        webhook_service.delete_outgoing_webhook(webhook.id)


@pytest.fixture(scope='module')
def channel(brand):
    channel_id = f'{brand.id}-test'
    url_prefix = 'https://acme.example.com/news/'

    channel = news_channel_service.create_channel(
        brand.id, channel_id, url_prefix
    )

    yield channel

    news_channel_service.delete_channel(channel_id)


@pytest.fixture(scope='module')
def item(channel, make_user):
    editor = make_user()
    slug = 'zieh-dir-das-rein'
    title = 'Zieh dir das rein!'
    body = 'any body'

    item = news_service.create_item(channel.id, slug, editor.id, title, body)

    yield item

    news_service.delete_item(item.id)
