"""
byceps.services.whereabouts.events
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2022-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from dataclasses import dataclass

from byceps.services.core.events import BaseEvent, EventParty
from byceps.services.user.models.user import User
from byceps.services.whereabouts.models import WhereaboutsClientID


@dataclass(frozen=True, kw_only=True)
class _WhereaboutsClientEvent(BaseEvent):
    client_id: WhereaboutsClientID


@dataclass(frozen=True, kw_only=True)
class WhereaboutsClientRegisteredEvent(_WhereaboutsClientEvent):
    pass


@dataclass(frozen=True, kw_only=True)
class WhereaboutsClientApprovedEvent(_WhereaboutsClientEvent):
    pass


@dataclass(frozen=True, kw_only=True)
class WhereaboutsClientDeletedEvent(_WhereaboutsClientEvent):
    pass


@dataclass(frozen=True, kw_only=True)
class WhereaboutsClientSignedOnEvent(_WhereaboutsClientEvent):
    pass


@dataclass(frozen=True, kw_only=True)
class WhereaboutsClientSignedOffEvent(_WhereaboutsClientEvent):
    pass


@dataclass(frozen=True, kw_only=True)
class WhereaboutsUnknownTagDetectedEvent(BaseEvent):
    client_id: WhereaboutsClientID
    client_location: str | None
    tag_identifier: str


@dataclass(frozen=True, kw_only=True)
class WhereaboutsStatusUpdatedEvent(BaseEvent):
    party: EventParty
    user: User
    whereabouts_description: str
