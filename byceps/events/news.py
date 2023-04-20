"""
byceps.events.news
~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from byceps.services.news.models import NewsChannelID, NewsItemID

from .base import _BaseEvent


@dataclass(frozen=True)
class NewsItemPublished(_BaseEvent):
    item_id: NewsItemID
    channel_id: NewsChannelID
    published_at: datetime
    title: str
    external_url: str | None
