"""
byceps.services.news.transfer.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime
from typing import NewType
from uuid import UUID

from attr import attrib, attrs

from ....typing import BrandID


ChannelID = NewType('ChannelID', str)


ItemID = NewType('ItemID', UUID)


ItemVersionID = NewType('ItemVersionID', UUID)


@attrs(frozen=True, slots=True)
class Channel:
    id = attrib(type=ChannelID)
    brand_id = attrib(type=BrandID)


@attrs(frozen=True, slots=True)
class Item:
    id = attrib(type=ItemID)
    slug = attrib(type=str)
    published_at = attrib(type=datetime)
    title = attrib(type=str)
    body = attrib(type=str)
    external_url = attrib(type=str)
    image_url = attrib(type=str)
