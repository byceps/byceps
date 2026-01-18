"""
byceps.services.user.log.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID

from byceps.services.user.models.user import User


UserLogEntryData = dict[str, Any]


@dataclass(frozen=True, kw_only=True)
class UserLogEntry:
    id: UUID
    occurred_at: datetime
    event_type: str
    user: User
    initiator: User | None
    data: UserLogEntryData
