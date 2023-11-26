"""
byceps.events.guest_server
~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from dataclasses import dataclass

from byceps.events.base import EventUser
from byceps.services.guest_server.models import ServerID
from byceps.services.party.models import PartyID

from .base import _BaseEvent


@dataclass(frozen=True)
class _GuestServerEvent(_BaseEvent):
    owner: EventUser
    server_id: ServerID


@dataclass(frozen=True)
class GuestServerRegisteredEvent(_GuestServerEvent):
    party_id: PartyID
    party_title: str


@dataclass(frozen=True)
class GuestServerApprovedEvent(_GuestServerEvent):
    pass


@dataclass(frozen=True)
class GuestServerCheckedInEvent(_GuestServerEvent):
    pass


@dataclass(frozen=True)
class GuestServerCheckedOutEvent(_GuestServerEvent):
    pass
