"""
byceps.services.user.transfer.log
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID

from ....typing import UserID


UserLogEntryData = dict[str, Any]


@dataclass(frozen=True)
class UserLogEntry:
    id: UUID
    occurred_at: datetime
    event_type: str
    user_id: UserID
    data: UserLogEntryData
