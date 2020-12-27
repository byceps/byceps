"""
byceps.announce.discord.news
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Announce news events on Discord.

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from ...events.news import NewsItemPublished
from ...services.news.transfer.models import ChannelID

from ._util import send_message


def announce_news_item_published(event: NewsItemPublished) -> None:
    """Announce that a news item has been published."""
    text = (
        f'Die News "{event.title}" wurde veröffentlicht. '
        f'{event.external_url}'
    )

    send_news_message(event.channel_id, text)


def send_news_message(channel_id: ChannelID, text: str) -> None:
    scope = 'news'
    scope_id = str(channel_id)

    send_message(scope, scope_id, text)
