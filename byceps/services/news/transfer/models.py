"""
byceps.services.news.transfer.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime
from typing import NewType
from uuid import UUID

from attr import attrib, attrs

from ....typing import BrandID, UserID


ChannelID = NewType('ChannelID', str)


ItemID = NewType('ItemID', UUID)


ItemVersionID = NewType('ItemVersionID', UUID)


ImageID = NewType('ImageID', UUID)


@attrs(frozen=True, slots=True)
class Channel:
    id = attrib(type=ChannelID)
    brand_id = attrib(type=BrandID)


@attrs(frozen=True, slots=True)
class Item:
    id = attrib(type=ItemID)
    slug = attrib(type=str)
    published_at = attrib(type=datetime)
    published = attrib(type=bool)
    title = attrib(type=str)
    body = attrib(type=str)
    external_url = attrib(type=str)
    image_url = attrib(type=str)
    images = attrib()  # List[Image]


@attrs(frozen=True, slots=True)
class Image:
    id = attrib(type=ImageID)
    created_at = attrib(type=datetime)
    creator_id = attrib(type=UserID)
    item_id = attrib(type=ItemID)
    filename = attrib(type=str)
    caption = attrib(type=str)
