"""
byceps.events.guest_server
~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from dataclasses import dataclass

from byceps.services.guest_server.models import ServerID
from byceps.typing import PartyID, UserID

from .base import _BaseEvent


@dataclass(frozen=True)
class GuestServerRegisteredEvent(_BaseEvent):
    party_id: PartyID
    party_title: str
    owner_id: UserID
    owner_screen_name: str | None
    server_id: ServerID
