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
from byceps.signals import news as news_signals

from .helpers import (
    assert_request_data,
    CHANNEL_ORGA_LOG,
    CHANNEL_PUBLIC,
    get_submitted_json,
    mocked_irc_bot,
)


def test_published_news_item_announced(app, item):
    expected_channel1 = CHANNEL_PUBLIC
    expected_channel2 = CHANNEL_ORGA_LOG
    expected_text = (
        'Die News "Zieh dir das rein!" wurde veröffentlicht. '
        + 'https://acme.example.com/news/zieh-dir-das-rein'
    )

    event = news_service.publish_item(item.id)

    with mocked_irc_bot() as mock:
        news_signals.item_published.send(None, event=event)

    actual1, actual2 = get_submitted_json(mock, 2)
    assert_request_data(actual1, expected_channel1, expected_text)
    assert_request_data(actual2, expected_channel2, expected_text)


# helpers


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
