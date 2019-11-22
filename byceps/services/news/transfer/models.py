"""
byceps.services.news.transfer.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime
from typing import List, NewType
from uuid import UUID

from attr import attrs

from ....typing import BrandID, UserID


ChannelID = NewType('ChannelID', str)


ItemID = NewType('ItemID', UUID)


ItemVersionID = NewType('ItemVersionID', UUID)


ImageID = NewType('ImageID', UUID)


@attrs(auto_attribs=True, frozen=True, slots=True)
class Channel:
    id: ChannelID
    brand_id: BrandID
    url_prefix: str


@attrs(auto_attribs=True, frozen=True, slots=True)
class Image:
    id: ImageID
    created_at: datetime
    creator_id: UserID
    item_id: ItemID
    filename: str
    alt_text: str
    caption: str


@attrs(auto_attribs=True, frozen=True, slots=True)
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
