"""
byceps.announce.irc.news
~~~~~~~~~~~~~~~~~~~~~~~~

Announce news events on IRC.

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from ...events.news import NewsItemPublished

from ._config import CHANNEL_ORGA_LOG, CHANNEL_PUBLIC
from ._util import send_message


def announce_news_item_published(event: NewsItemPublished) -> None:
    """Announce that a news item has been published."""
    text = (
        f'Die News "{event.title}" wurde veröffentlicht. {event.external_url}'
    )

    send_news_message(event, CHANNEL_PUBLIC, text)
    send_news_message(event, CHANNEL_ORGA_LOG, text)


# helpers


def send_news_message(
    event: NewsItemPublished, channel: str, text: str
) -> None:
    scope = 'news'
    scope_id = str(event.channel_id)

    send_message(event, scope, scope_id, channel, text)
