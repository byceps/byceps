"""
byceps.services.ticketing.transfer.log
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID

from .models import TicketID


TicketLogEntryData = dict[str, Any]


@dataclass(frozen=True)
class TicketLogEntry:
    id: UUID
    occurred_at: datetime
    event_type: str
    ticket_id: TicketID
    data: TicketLogEntryData
