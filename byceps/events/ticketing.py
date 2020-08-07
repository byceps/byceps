"""
byceps.events.ticketing
~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from dataclasses import dataclass
from typing import Optional

from ..services.ticketing.transfer.models import TicketID
from ..typing import UserID

from .base import _BaseEvent


@dataclass(frozen=True)
class _TicketEvent(_BaseEvent):
    initiator_id: Optional[UserID]
    ticket_id: TicketID


@dataclass(frozen=True)
class TicketCheckedIn(_TicketEvent):
    pass
