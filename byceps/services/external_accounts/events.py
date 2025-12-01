"""
byceps.services.connected_external_accounts.events
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from uuid import UUID

from byceps.services.core.events import BaseEvent
from byceps.services.user.models.user import User


@dataclass(frozen=True, kw_only=True)
class _ExternalAccountConnectionEvent(BaseEvent):
    connected_external_account_id: UUID
    user: User
    service: str
    external_id: str | None
    external_name: str | None


@dataclass(frozen=True, kw_only=True)
class ExternalAccountConnectedEvent(_ExternalAccountConnectionEvent):
    pass


@dataclass(frozen=True, kw_only=True)
class ExternalAccountDisconnectedEvent(_ExternalAccountConnectionEvent):
    pass
