"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import Flask
import pytest

from byceps.announce.connections import build_announcement_request
from byceps.events.news import NewsItemPublishedEvent
from byceps.services.brand.models import Brand
from byceps.services.news.models import NewsChannel, NewsItemID
from byceps.services.site.models import Site
from byceps.services.user.models.user import User
from byceps.services.webhooks.models import OutgoingWebhook

from tests.helpers import generate_uuid

from .helpers import build_announcement_request_for_discord, build_webhook, now


OCCURRED_AT = now()
NEWS_ITEM_ID = NewsItemID(generate_uuid())


def test_published_news_item_announced_with_url(
    admin_app: Flask, admin_user: User, channel_with_site: NewsChannel
) -> None:
    expected_content = (
        '[News] Die News "Zieh dir das mal rein!" wurde veröffentlicht. '
        'https://www.acmecon.test/news/zieh-dir-das-mal-rein'
    )
    expected = build_announcement_request_for_discord(expected_content)

    event = NewsItemPublishedEvent(
        occurred_at=OCCURRED_AT,
        initiator_id=admin_user.id,
        initiator_screen_name=admin_user.screen_name,
        item_id=NEWS_ITEM_ID,
        channel_id=channel_with_site.id,
        published_at=OCCURRED_AT,
        title='Zieh dir das mal rein!',
        external_url='https://www.acmecon.test/news/zieh-dir-das-mal-rein',
    )

    webhook = build_news_webhook(channel_with_site)

    assert build_announcement_request(event, webhook) == expected


def test_published_news_item_announced_without_url(
    admin_app: Flask, admin_user: User, channel_without_site: NewsChannel
) -> None:
    expected_content = (
        '[News] Die News "Zieh dir auch das rein!" wurde veröffentlicht.'
    )
    expected = build_announcement_request_for_discord(expected_content)

    event = NewsItemPublishedEvent(
        occurred_at=OCCURRED_AT,
        initiator_id=admin_user.id,
        initiator_screen_name=admin_user.screen_name,
        item_id=NEWS_ITEM_ID,
        channel_id=channel_without_site.id,
        published_at=OCCURRED_AT,
        title='Zieh dir auch das rein!',
        external_url=None,
    )

    webhook = build_news_webhook(channel_without_site)

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


@pytest.fixture()
def channel_with_site(
    brand: Brand, site: Site, make_news_channel
) -> NewsChannel:
    return make_news_channel(brand.id, announcement_site_id=site.id)


@pytest.fixture()
def channel_without_site(brand: Brand, make_news_channel) -> NewsChannel:
    return make_news_channel(brand.id)
