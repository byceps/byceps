"""
byceps.announce.discord.connections
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Announce events on Discord.

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Optional

from ...events.base import _BaseEvent
from ...events.board import BoardPostingCreated, BoardTopicCreated
from ...events.news import NewsItemPublished
from ...signals import board as board_signals
from ...signals import news as news_signals
from ...util.jobqueue import enqueue

from ..handlers import board, news
from ..helpers import get_webhooks


EVENT_TYPES_TO_HANDLERS = {
    BoardTopicCreated: board.announce_board_topic_created,
    BoardPostingCreated: board.announce_board_posting_created,
    NewsItemPublished: news.announce_news_item_published,
}


@board_signals.topic_created.connect
@board_signals.posting_created.connect
@news_signals.item_published.connect
def _on_event(sender, *, event: Optional[_BaseEvent] = None) -> None:
    event_type = type(event)

    handler = EVENT_TYPES_TO_HANDLERS.get(event_type)
    if handler is None:
        return None

    webhook_format = 'discord'
    webhooks = get_webhooks(event, webhook_format)
    for webhook in webhooks:
        enqueue(handler, event, webhook)
