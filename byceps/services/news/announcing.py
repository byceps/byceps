"""
byceps.services.news.announcing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Announce news events.

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from functools import wraps

from flask_babel import gettext

from byceps.announce.helpers import matches_selectors, with_locale
from byceps.services.webhooks.models import Announcement, OutgoingWebhook

from .events import NewsItemPublishedEvent


def apply_selectors(handler):
    @wraps(handler)
    def wrapper(
        event_name: str, event: NewsItemPublishedEvent, webhook: OutgoingWebhook
    ) -> Announcement | None:
        channel_id = str(event.channel_id)
        if not matches_selectors(event_name, webhook, 'channel_id', channel_id):
            return None

        return handler(event_name, event, webhook)

    return wrapper


@apply_selectors
@with_locale
def announce_news_item_published(
    event_name: str, event: NewsItemPublishedEvent, webhook: OutgoingWebhook
) -> Announcement | None:
    """Announce that a news item has been published."""
    text = gettext(
        'The news "%(title)s" has been published.', title=event.title
    )

    if event.external_url is not None:
        text += f' {event.external_url}'

    if event.published_at > event.occurred_at:
        # Announce later.
        return Announcement(text, announce_at=event.published_at)
    else:
        # Announce now.
        return Announcement(text)
