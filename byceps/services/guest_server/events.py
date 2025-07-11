"""
byceps.services.guest_server.events
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass

from byceps.services.core.events import _BaseEvent, EventParty, EventUser
from byceps.services.guest_server.models import ServerID


@dataclass(frozen=True, kw_only=True)
class _GuestServerEvent(_BaseEvent):
    owner: EventUser
    server_id: ServerID


@dataclass(frozen=True, kw_only=True)
class GuestServerRegisteredEvent(_GuestServerEvent):
    party: EventParty


@dataclass(frozen=True, kw_only=True)
class GuestServerApprovedEvent(_GuestServerEvent):
    pass


@dataclass(frozen=True, kw_only=True)
class GuestServerCheckedInEvent(_GuestServerEvent):
    pass


@dataclass(frozen=True, kw_only=True)
class GuestServerCheckedOutEvent(_GuestServerEvent):
    pass
