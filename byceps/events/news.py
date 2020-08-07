"""
byceps.events.news
~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from dataclasses import dataclass
from typing import Optional

from ..services.news.transfer.models import ItemID
from ..typing import UserID

from .base import _BaseEvent


@dataclass(frozen=True)
class NewsItemPublished(_BaseEvent):
    initiator_id: Optional[UserID]
    item_id: ItemID
