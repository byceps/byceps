"""
byceps.events.news
~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from dataclasses import dataclass

from ..news.transfer.models import ItemID


@dataclass(frozen=True)
class NewsItemPublished:
    item_id: ItemID
