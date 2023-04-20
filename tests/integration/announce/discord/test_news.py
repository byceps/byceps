"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import Flask
import pytest

from byceps.announce.connections import build_announcement_request
from byceps.services.brand.models import Brand
from byceps.services.news import news_item_service
from byceps.services.news.models import BodyFormat, NewsChannel, NewsItem
from byceps.services.site.models import Site
from byceps.services.webhooks.models import OutgoingWebhook

from .helpers import build_announcement_request_for_discord, build_webhook


def test_published_news_item_announced_with_url(
    admin_app: Flask, item_with_url: NewsItem
) -> None:
    expected_content = (
        '[News] Die News "Zieh dir das rein!" wurde veröffentlicht. '
        + 'https://www.acmecon.test/news/zieh-dir-das-rein'
    )
    expected = build_announcement_request_for_discord(expected_content)

    event = news_item_service.publish_item(item_with_url.id)

    webhook = build_news_webhook(item_with_url.channel)

    assert build_announcement_request(event, webhook) == expected


def test_published_news_item_announced_without_url(
    admin_app: Flask, item_without_url: NewsItem
) -> None:
    expected_content = (
        '[News] Die News "Zieh dir auch das rein!" wurde veröffentlicht.'
    )
    expected = build_announcement_request_for_discord(expected_content)

    event = news_item_service.publish_item(item_without_url.id)

    webhook = build_news_webhook(item_without_url.channel)

    assert build_announcement_request(event, webhook) == expected


# helpers


def build_news_webhook(channel: NewsChannel) -> OutgoingWebhook:
    return build_webhook(
        event_types={'news-item-published'},
        event_filters={
            'news-item-published': {'channel_id': [str(channel.id)]}
        },
        text_prefix='[News] ',
        url='https://webhoooks.test/news',
    )


@pytest.fixture
def channel_with_site(
    brand: Brand, site: Site, make_news_channel
) -> NewsChannel:
    return make_news_channel(brand.id, announcement_site_id=site.id)


@pytest.fixture
def channel_without_site(brand: Brand, make_news_channel) -> NewsChannel:
    return make_news_channel(brand.id)


@pytest.fixture
def make_item(make_user):
    def _wrapper(channel: NewsChannel, slug: str, title: str) -> NewsItem:
        editor = make_user()
        body = 'any body'
        body_format = BodyFormat.html

        return news_item_service.create_item(
            channel.id, slug, editor.id, title, body, body_format
        )

    return _wrapper


@pytest.fixture
def item_with_url(make_item, channel_with_site: NewsChannel) -> NewsItem:
    slug = 'zieh-dir-das-rein'
    title = 'Zieh dir das rein!'

    return make_item(channel_with_site, slug, title)


@pytest.fixture
def item_without_url(make_item, channel_without_site: NewsChannel) -> NewsItem:
    slug = 'zieh-dir-auch-das-rein'
    title = 'Zieh dir auch das rein!'

    return make_item(channel_without_site, slug, title)
