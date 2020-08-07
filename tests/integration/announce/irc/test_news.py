"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import pytest

from byceps.announce.irc import news  # Load signal handlers.
import byceps.blueprints.news.signals as news_signals
from byceps.events.news import NewsItemPublished
from byceps.services.news import (
    channel_service as news_channel_service,
    service as news_service,
)

from .helpers import (
    assert_submitted_data,
    CHANNEL_ORGA_LOG,
    CHANNEL_PUBLIC,
    mocked_irc_bot,
    now,
)


def test_published_news_item_announced(app, item, editor):
    expected_channels = [CHANNEL_ORGA_LOG, CHANNEL_PUBLIC]
    expected_text = (
        'ACME Entertainment Convention: '
        + 'Die News "Zieh dir das rein!" wurde veröffentlicht. '
        + 'https://acme.example.com/news/zieh-dir-das-rein'
    )

    with mocked_irc_bot() as mock:
        event = NewsItemPublished(
            occurred_at=now(), initiator_id=editor.id, item_id=item.id
        )
        news_signals.item_published.send(None, event=event)
        assert_submitted_data(mock, expected_channels, expected_text)


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
def editor(make_user):
    return make_user('Karla_Kolumna')


@pytest.fixture(scope='module')
def item(channel, editor):
    slug = 'zieh-dir-das-rein'
    title = 'Zieh dir das rein!'
    body = 'any body'

    item = news_service.create_item(channel.id, slug, editor.id, title, body)

    yield item

    news_service.delete_item(item.id)
