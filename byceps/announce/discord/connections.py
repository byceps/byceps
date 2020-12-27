"""
byceps.announce.discord.connections
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Announce events on Discord.

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Optional

from ...events.board import BoardPostingCreated, BoardTopicCreated
from ...events.news import NewsItemPublished
from ...signals import board as board_signals
from ...signals import news as news_signals
from ...util.jobqueue import enqueue

from . import board, news


# board


@board_signals.topic_created.connect
def _on_board_topic_created(
    sender, *, event: Optional[BoardTopicCreated] = None
) -> None:
    enqueue(board.announce_board_topic_created, event)


@board_signals.posting_created.connect
def _on_board_posting_created(
    sender, *, event: Optional[BoardPostingCreated] = None
) -> None:
    enqueue(board.announce_board_posting_created, event)


# news


@news_signals.item_published.connect
def _on_news_item_published(
    sender, *, event: Optional[NewsItemPublished] = None
) -> None:
    enqueue(news.announce_news_item_published, event)
