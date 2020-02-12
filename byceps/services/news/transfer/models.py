"""
byceps.services.news.transfer.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, NewType
from uuid import UUID

from ....typing import BrandID, UserID


ChannelID = NewType('ChannelID', str)


ItemID = NewType('ItemID', UUID)


ItemVersionID = NewType('ItemVersionID', UUID)


ImageID = NewType('ImageID', UUID)


@dataclass(frozen=True)
class Channel:
    id: ChannelID
    brand_id: BrandID
    url_prefix: str


@dataclass(frozen=True)
class Image:
    id: ImageID
    created_at: datetime
    creator_id: UserID
    item_id: ItemID
    filename: str
    alt_text: str
    caption: str
    attribution: str


@dataclass(frozen=True)
class Item:
    id: ItemID
    channel: Channel
    slug: str
    published_at: datetime
    published: bool
    title: str
    body: str
    external_url: str
    image_url_path: str
    images: List[Image]
