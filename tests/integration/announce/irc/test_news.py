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
from byceps.signals import news as news_signals

from tests.integration.services.news.conftest import make_channel

from .helpers import (
    assert_request_data,
    CHANNEL_INTERNAL,
    CHANNEL_PUBLIC,
    get_submitted_json,
    mocked_irc_bot,
)


def test_published_news_item_announced(app: Flask, item: Item) -> None:
    expected_channel1 = CHANNEL_PUBLIC
    expected_channel2 = CHANNEL_INTERNAL
    expected_text = (
        'Die News "Zieh dir das mal rein!" wurde veröffentlicht. '
        + 'https://acme.example.com/news/zieh-dir-das-mal-rein'
    )

    event = news_service.publish_item(item.id)

    with mocked_irc_bot() as mock:
        news_signals.item_published.send(None, event=event)

    actual1, actual2 = get_submitted_json(mock, 2)
    assert_request_data(actual1, expected_channel1, expected_text)
    assert_request_data(actual2, expected_channel2, expected_text)


# helpers


@pytest.fixture
def channel(brand: Brand, make_channel) -> Channel:
    url_prefix = 'https://acme.example.com/news/'

    return make_channel(brand.id, url_prefix=url_prefix)


@pytest.fixture
def item(channel: Channel, make_user) -> Item:
    editor = make_user()
    slug = 'zieh-dir-das-mal-rein'
    title = 'Zieh dir das mal rein!'
    body = 'any body'
    body_format = BodyFormat.html

    return news_service.create_item(
        channel.id, slug, editor.id, title, body, body_format
    )
