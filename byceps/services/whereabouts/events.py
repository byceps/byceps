"""
byceps.services.whereabouts.events
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2022-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from dataclasses import dataclass

from byceps.services.core.events import _BaseEvent, EventParty, EventUser
from byceps.services.whereabouts.models import WhereaboutsClientID


@dataclass(frozen=True, kw_only=True)
class _WhereaboutsClientEvent(_BaseEvent):
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
class WhereaboutsStatusUpdatedEvent(_BaseEvent):
    party: EventParty
    user: EventUser
    whereabouts_description: str
