"""
byceps.services.newsletter.transfer.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime
from typing import NewType

from attr import attrs

from ....typing import UserID


ListID = NewType('ListID', str)


@attrs(auto_attribs=True, frozen=True, slots=True)
class List:
    id: ListID
    title: str


@attrs(auto_attribs=True, frozen=True, slots=True)
class Subscription:
    user_id: UserID
    list_id: ListID
    expressed_at: datetime
