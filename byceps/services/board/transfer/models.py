"""
byceps.services.board.transfer.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

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
