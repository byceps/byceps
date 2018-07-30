"""
byceps.services.board.transfer.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime
from typing import NewType
from uuid import UUID

from attr import attrib, attrs

from ....typing import BrandID


BoardID = NewType('BoardID', str)


CategoryID = NewType('CategoryID', UUID)


PostingID = NewType('PostingID', UUID)


TopicID = NewType('TopicID', UUID)


@attrs(frozen=True, slots=True)
class Board:
    id = attrib(type=BoardID)
    brand_id = attrib(type=BrandID)


@attrs(frozen=True, slots=True)
class Category:
    id = attrib(type=CategoryID)
    board_id = attrib(type=BoardID)
    position = attrib(type=int)
    slug = attrib(type=str)
    title = attrib(type=str)
    description = attrib(type=str)
    topic_count = attrib(type=int)
    posting_count = attrib(type=int)


@attrs(frozen=True, slots=True)
class CategoryWithLastUpdate(Category):
    last_posting_updated_at = attrib(type=datetime)
    last_posting_updated_by = attrib()
