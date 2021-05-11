"""
byceps.services.news.transfer.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import NewType, Optional
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
    number: int
    filename: str
    url_path: str
    alt_text: Optional[str]
    caption: Optional[str]
    attribution: Optional[str]


@dataclass(frozen=True)
class Item:
    id: ItemID
    channel: Channel
    slug: str
    published_at: Optional[datetime]
    published: bool
    title: str
    body: str
    external_url: str
    image_url_path: Optional[str]
    images: list[Image]


@dataclass(frozen=True)
class Headline:
    slug: str
    published_at: Optional[datetime]
    title: str
