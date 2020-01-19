"""
byceps.services.newsletter.transfer.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import NewType

from ....typing import UserID


ListID = NewType('ListID', str)


@dataclass(frozen=True)
class List:
    id: ListID
    title: str


@dataclass(frozen=True)
class Subscription:
    user_id: UserID
    list_id: ListID
    expressed_at: datetime
