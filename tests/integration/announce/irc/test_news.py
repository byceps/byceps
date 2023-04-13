"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import Flask
import pytest

from byceps.announce.connections import build_announcement_request
from byceps.services.brand.models import Brand
from byceps.services.news.models import BodyFormat, NewsChannel, NewsItem
from byceps.services.news import news_item_service
from byceps.services.site.models import Site

from .helpers import build_announcement_request_for_irc


def test_published_news_item_announced_with_url(
    admin_app: Flask, item_with_url: NewsItem, webhook_for_irc
) -> None:
    expected_text = (
        'Die News "Zieh dir das mal rein!" wurde veröffentlicht. '
        + 'https://www.acmecon.test/news/zieh-dir-das-mal-rein'
    )
    expected = build_announcement_request_for_irc(expected_text)

    event = news_item_service.publish_item(item_with_url.id)

    assert build_announcement_request(event, webhook_for_irc) == expected


def test_published_news_item_announced_without_url(
    admin_app: Flask, item_without_url: NewsItem, webhook_for_irc
) -> None:
    expected_text = (
        'Die News "Zieh dir auch das mal rein!" wurde veröffentlicht.'
    )
    expected = build_announcement_request_for_irc(expected_text)

    event = news_item_service.publish_item(item_without_url.id)

    assert build_announcement_request(event, webhook_for_irc) == expected


# helpers


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
    slug = 'zieh-dir-das-mal-rein'
    title = 'Zieh dir das mal rein!'

    return make_item(channel_with_site, slug, title)


@pytest.fixture
def item_without_url(make_item, channel_without_site: NewsChannel) -> NewsItem:
    slug = 'zieh-dir-auch-das-mal-rein'
    title = 'Zieh dir auch das mal rein!'

    return make_item(channel_without_site, slug, title)
