"""
:Copyright: 2006-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import Flask
import pytest

import byceps.announce.connections  # Connect signal handlers.
from byceps.services.brand.transfer.models import Brand
from byceps.services.news import service as news_service
from byceps.services.news.transfer.models import BodyFormat, Channel, Item
from byceps.services.site.transfer.models import Site
from byceps.services.webhooks import service as webhook_service
from byceps.signals import news as news_signals

from tests.integration.services.news.conftest import make_channel

from .helpers import assert_request, mocked_webhook_receiver


WEBHOOK_URL = 'https://webhoooks.test/news'


def test_published_news_item_announced_with_url(
    admin_app: Flask, item_with_url: Item
) -> None:
    expected_content = (
        '[News] Die News "Zieh dir das rein!" wurde veröffentlicht. '
        + 'https://www.acmecon.test/news/zieh-dir-das-rein'
    )

    create_webhooks(item_with_url.channel)

    event = news_service.publish_item(item_with_url.id)

    with mocked_webhook_receiver(WEBHOOK_URL) as mock:
        news_signals.item_published.send(None, event=event)

    assert_request(mock, expected_content)


def test_published_news_item_announced_without_url(
    admin_app: Flask, item_without_url: Item
) -> None:
    expected_content = (
        '[News] Die News "Zieh dir auch das rein!" wurde veröffentlicht.'
    )

    create_webhooks(item_without_url.channel)

    event = news_service.publish_item(item_without_url.id)

    with mocked_webhook_receiver(WEBHOOK_URL) as mock:
        news_signals.item_published.send(None, event=event)

    assert_request(mock, expected_content)


# helpers


@pytest.fixture
def channel_with_site(brand: Brand, site: Site, make_channel) -> Channel:
    return make_channel(brand.id, announcement_site_id=site.id)


@pytest.fixture
def channel_without_site(brand: Brand, make_channel) -> Channel:
    return make_channel(brand.id)


def create_webhooks(channel: Channel) -> None:
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
def make_item(make_user):
    def _wrapper(channel: Channel, slug: str, title: str) -> Item:
        editor = make_user()
        body = 'any body'
        body_format = BodyFormat.html

        return news_service.create_item(
            channel.id, slug, editor.id, title, body, body_format
        )

    return _wrapper


@pytest.fixture
def item_with_url(make_item, channel_with_site: Channel) -> Item:
    slug = 'zieh-dir-das-rein'
    title = 'Zieh dir das rein!'

    return make_item(channel_with_site, slug, title)


@pytest.fixture
def item_without_url(make_item, channel_without_site: Channel) -> Item:
    slug = 'zieh-dir-auch-das-rein'
    title = 'Zieh dir auch das rein!'

    return make_item(channel_without_site, slug, title)
