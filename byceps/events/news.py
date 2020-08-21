"""
byceps.events.news
~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from dataclasses import dataclass

from ..services.news.transfer.models import ChannelID, ItemID

from .base import _BaseEvent


@dataclass(frozen=True)
class NewsItemPublished(_BaseEvent):
    item_id: ItemID
    channel_id: ChannelID
    title: str
    external_url: str
