"""
byceps.services.news.events
~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from datetime import datetime

from byceps.services.core.events import BaseEvent
from byceps.services.news.models import NewsChannelID, NewsItemID


@dataclass(frozen=True, kw_only=True)
class NewsItemPublishedEvent(BaseEvent):
    item_id: NewsItemID
    channel_id: NewsChannelID
    published_at: datetime
    title: str
    external_url: str | None
