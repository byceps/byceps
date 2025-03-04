"""
byceps.services.connected_external_accounts.events
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from uuid import UUID

from byceps.services.core.events import _BaseEvent, EventUser


@dataclass(frozen=True)
class _ExternalAccountConnectionEvent(_BaseEvent):
    connected_external_account_id: UUID
    user: EventUser
    service: str
    external_id: str | None
    external_name: str | None


@dataclass(frozen=True)
class ExternalAccountConnectedEvent(_ExternalAccountConnectionEvent):
    pass


@dataclass(frozen=True)
class ExternalAccountDisconnectedEvent(_ExternalAccountConnectionEvent):
    pass
