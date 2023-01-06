"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import Flask
import pytest

import byceps.announce.connections  # Connect signal handlers.  # noqa: F401
from byceps.services.brand.transfer.models import Brand
from byceps.services.news import news_item_service
from byceps.services.news.transfer.models import BodyFormat, Channel, Item
from byceps.services.site.transfer.models import Site
from byceps.signals import news as news_signals

from .helpers import assert_submitted_text, mocked_irc_bot


def test_published_news_item_announced_with_url(
    app: Flask, item_with_url: Item
) -> None:
    expected_text = (
        'Die News "Zieh dir das mal rein!" wurde veröffentlicht. '
        + 'https://www.acmecon.test/news/zieh-dir-das-mal-rein'
    )

    event = news_item_service.publish_item(item_with_url.id)

    with mocked_irc_bot() as mock:
        news_signals.item_published.send(None, event=event)

    assert_submitted_text(mock, expected_text)


def test_published_news_item_announced_without_url(
    app: Flask, item_without_url: Item
) -> None:
    expected_text = (
        'Die News "Zieh dir auch das mal rein!" wurde veröffentlicht.'
    )

    event = news_item_service.publish_item(item_without_url.id)

    with mocked_irc_bot() as mock:
        news_signals.item_published.send(None, event=event)

    assert_submitted_text(mock, expected_text)


# helpers


@pytest.fixture
def channel_with_site(brand: Brand, site: Site, make_news_channel) -> Channel:
    return make_news_channel(brand.id, announcement_site_id=site.id)


@pytest.fixture
def channel_without_site(brand: Brand, make_news_channel) -> Channel:
    return make_news_channel(brand.id)


@pytest.fixture
def make_item(make_user):
    def _wrapper(channel: Channel, slug: str, title: str) -> Item:
        editor = make_user()
        body = 'any body'
        body_format = BodyFormat.html

        return news_item_service.create_item(
            channel.id, slug, editor.id, title, body, body_format
        )

    return _wrapper


@pytest.fixture
def item_with_url(make_item, channel_with_site: Channel) -> Item:
    slug = 'zieh-dir-das-mal-rein'
    title = 'Zieh dir das mal rein!'

    return make_item(channel_with_site, slug, title)


@pytest.fixture
def item_without_url(make_item, channel_without_site: Channel) -> Item:
    slug = 'zieh-dir-auch-das-mal-rein'
    title = 'Zieh dir auch das mal rein!'

    return make_item(channel_without_site, slug, title)
