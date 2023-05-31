"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import Flask

from byceps.announce.connections import build_announcement_request
from byceps.events.news import NewsItemPublishedEvent
from byceps.services.news.models import NewsChannelID, NewsItemID
from byceps.services.user.models.user import User

from tests.helpers import generate_token, generate_uuid

from .helpers import build_announcement_request_for_irc, now


OCCURRED_AT = now()
NEWS_CHANNEL_ID = NewsChannelID(generate_token())
NEWS_ITEM_ID = NewsItemID(generate_uuid())


def test_published_news_item_announced_with_url(
    admin_app: Flask, admin_user: User, webhook_for_irc
) -> None:
    expected_text = (
        'Die News "Zieh dir das mal rein!" wurde veröffentlicht. '
        'https://www.acmecon.test/news/zieh-dir-das-mal-rein'
    )
    expected = build_announcement_request_for_irc(expected_text)

    event = NewsItemPublishedEvent(
        occurred_at=OCCURRED_AT,
        initiator_id=admin_user.id,
        initiator_screen_name=admin_user.screen_name,
        item_id=NEWS_ITEM_ID,
        channel_id=NEWS_CHANNEL_ID,
        published_at=OCCURRED_AT,
        title='Zieh dir das mal rein!',
        external_url='https://www.acmecon.test/news/zieh-dir-das-mal-rein',
    )

    assert build_announcement_request(event, webhook_for_irc) == expected


def test_published_news_item_announced_without_url(
    admin_app: Flask, admin_user: User, webhook_for_irc
) -> None:
    expected_text = 'Die News "Zieh dir auch das rein!" wurde veröffentlicht.'
    expected = build_announcement_request_for_irc(expected_text)

    event = NewsItemPublishedEvent(
        occurred_at=OCCURRED_AT,
        initiator_id=admin_user.id,
        initiator_screen_name=admin_user.screen_name,
        item_id=NEWS_ITEM_ID,
        channel_id=NEWS_CHANNEL_ID,
        published_at=OCCURRED_AT,
        title='Zieh dir auch das rein!',
        external_url=None,
    )

    assert build_announcement_request(event, webhook_for_irc) == expected
