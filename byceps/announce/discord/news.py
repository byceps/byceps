"""
byceps.announce.discord.news
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Announce news events on Discord.

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Optional

from ...events.news import NewsItemPublished
from ...services.news.transfer.models import ChannelID
from ...signals import news as news_signals
from ...util.jobqueue import enqueue

from ._util import send_message


@news_signals.item_published.connect
def _on_news_item_published(
    sender, *, event: Optional[NewsItemPublished] = None
) -> None:
    enqueue(announce_news_item_published, event)


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
