"""
byceps.events.guest_server
~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from typing import Optional

from ..services.guest_server.transfer.models import ServerID
from ..typing import PartyID, UserID

from .base import _BaseEvent


@dataclass(frozen=True)
class GuestServerRegistered(_BaseEvent):
    party_id: PartyID
    owner_id: UserID
    owner_screen_name: Optional[str]
    server_id: ServerID
