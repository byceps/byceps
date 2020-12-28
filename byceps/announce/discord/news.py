"""
byceps.announce.discord.news
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Announce news events on Discord.

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from ...events.news import NewsItemPublished
from ...services.webhooks.transfer.models import OutgoingWebhook

from ..common import news
from ..helpers import call_webhook, match_scope


def announce_news_item_published(
    event: NewsItemPublished, webhook: OutgoingWebhook
) -> None:
    """Announce that a news item has been published."""
    text = news.assemble_text_for_news_item_published(event)

    send_news_message(event, webhook, text)


# helpers


def send_news_message(
    event: NewsItemPublished, webhook: OutgoingWebhook, text: str
) -> None:
    scope = 'news'
    scope_id = str(event.channel_id)

    if not match_scope(webhook, scope, scope_id):
        return

    call_webhook(webhook, text)
