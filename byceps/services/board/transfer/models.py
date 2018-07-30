"""
byceps.services.board.transfer.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import NewType
from uuid import UUID


BoardID = NewType('BoardID', str)


CategoryID = NewType('CategoryID', UUID)


PostingID = NewType('PostingID', UUID)


TopicID = NewType('TopicID', UUID)
