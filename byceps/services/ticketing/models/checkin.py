"""
byceps.services.ticketing.models.checkin
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from byceps.typing import UserID

from .ticket import TicketID


@dataclass(frozen=True)
class TicketCheckIn:
    id: UUID
    occurred_at: datetime
    ticket_id: TicketID
    initiator_id: UserID
