"""
byceps.announce.handlers.news
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Announce news events.

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from functools import wraps
from typing import Optional

from ...events.news import NewsItemPublished
from ...services.webhooks.models import OutgoingWebhook

from ..helpers import Announcement, matches_selectors
from ..text_assembly import news


def apply_selectors(handler):
    @wraps(handler)
    def wrapper(
        event: NewsItemPublished, webhook: OutgoingWebhook
    ) -> Optional[Announcement]:
        channel_id = str(event.channel_id)
        if not matches_selectors(event, webhook, 'channel_id', channel_id):
            return None

        return handler(event, webhook)

    return wrapper


@apply_selectors
def announce_news_item_published(
    event: NewsItemPublished, webhook: OutgoingWebhook
) -> Optional[Announcement]:
    """Announce that a news item has been published."""
    text = news.assemble_text_for_news_item_published(event)

    if event.published_at > event.occurred_at:
        # Announce later.
        return Announcement(text, announce_at=event.published_at)
    else:
        # Announce now.
        return Announcement(text)
