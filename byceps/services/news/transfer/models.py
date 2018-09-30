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


ItemID = NewType('ItemID', UUID)


ItemVersionID = NewType('ItemVersionID', UUID)


@attrs(frozen=True, slots=True)
class Item:
    id = attrib(type=ItemID)
    slug = attrib(type=str)
    published_at = attrib(type=datetime)
    title = attrib(type=str)
    body = attrib(type=str)
    external_url = attrib(type=str)
    image_url = attrib(type=str)
