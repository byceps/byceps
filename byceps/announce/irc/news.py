"""
byceps.announce.irc.news
~~~~~~~~~~~~~~~~~~~~~~~~

Announce news events on IRC.

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from ...events.news import NewsItemPublished
from ...services.brand import service as brand_service
from ...services.news import channel_service as news_channel_service

from ..helpers import get_screen_name_or_fallback

from ._config import CHANNEL_ORGA_LOG, CHANNEL_PUBLIC
from ._util import send_message


def announce_news_item_published(event: NewsItemPublished) -> None:
    announce_news_item_published_publicly(event)
    announce_news_item_published_internally(event)


def announce_news_item_published_publicly(event: NewsItemPublished) -> None:
    """Announce publicly that a news item has been published."""
    channel = news_channel_service.find_channel(event.channel_id)
    brand = brand_service.find_brand(channel.brand_id)

    text = (
        f'{brand.title}: Die News "{event.title}" wurde veröffentlicht. '
        f'{event.external_url}'
    )

    send_message(CHANNEL_PUBLIC, text)


def announce_news_item_published_internally(event: NewsItemPublished) -> None:
    """Announce internally that a news item has been published."""
    initiator_screen_name = get_screen_name_or_fallback(
        event.initiator_screen_name
    )

    text = (
        f'{initiator_screen_name} hat die News "{event.title}" veröffentlicht. '
        f'{event.external_url}'
    )

    send_message(CHANNEL_ORGA_LOG, text)
