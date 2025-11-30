"""
byceps.services.ticketing.log.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID

from byceps.services.ticketing.models.ticket import TicketID


TicketLogEntryData = dict[str, Any]


@dataclass(frozen=True, kw_only=True)
class TicketLogEntry:
    id: UUID
    occurred_at: datetime
    event_type: str
    ticket_id: TicketID
    data: TicketLogEntryData
