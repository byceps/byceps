"""
byceps.services.board.transfer.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime
from typing import NewType
from uuid import UUID

from attr import attrs

from ....typing import BrandID

from ...user.transfer.models import User


BoardID = NewType('BoardID', str)


CategoryID = NewType('CategoryID', UUID)


PostingID = NewType('PostingID', UUID)


TopicID = NewType('TopicID', UUID)


@attrs(auto_attribs=True, frozen=True, slots=True)
class Board:
    id: BoardID
    brand_id: BrandID
    access_restricted: bool


@attrs(auto_attribs=True, frozen=True, slots=True)
class Category:
    id: CategoryID
    board_id: BoardID
    position: int
    slug: str
    title: str
    description: str
    topic_count: int
    posting_count: int
    hidden: bool


@attrs(auto_attribs=True, frozen=True, slots=True)
class CategoryWithLastUpdate(Category):
    last_posting_updated_at: datetime
    last_posting_updated_by: User
