"""
byceps.services.whereabouts.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2022-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from ipaddress import IPv4Address, IPv6Address
from typing import NewType
from uuid import UUID

from byceps.services.party.models import Party
from byceps.services.user.models.user import User


WhereaboutsClientConfigID = NewType('WhereaboutsClientConfigID', UUID)


WhereaboutsClientID = NewType('WhereaboutsClientID', UUID)


WhereaboutsID = NewType('WhereaboutsID', UUID)


IPAddress = IPv4Address | IPv6Address


@dataclass(frozen=True, kw_only=True)
class WhereaboutsClientConfig:
    id: WhereaboutsClientConfigID
    title: str
    description: str | None
    content: str


WhereaboutsClientAuthorityStatus = Enum(
    'WhereaboutsClientAuthorityStatus', ['pending', 'approved', 'deleted']
)


@dataclass(frozen=True, kw_only=True)
class WhereaboutsClientCandidate:
    id: WhereaboutsClientID
    registered_at: datetime
    button_count: int
    audio_output: bool
    token: str


@dataclass(frozen=True, kw_only=True)
class WhereaboutsClient:
    id: WhereaboutsClientID
    registered_at: datetime
    button_count: int
    audio_output: bool
    authority_status: WhereaboutsClientAuthorityStatus
    token: str | None
    name: str | None
    location: str | None
    description: str | None
    config_id: WhereaboutsClientConfigID | None

    @property
    def pending(self) -> bool:
        return self.authority_status == WhereaboutsClientAuthorityStatus.pending

    @property
    def approved(self) -> bool:
        return (
            self.authority_status == WhereaboutsClientAuthorityStatus.approved
        )


@dataclass(frozen=True, kw_only=True)
class WhereaboutsClientWithLivelinessStatus(WhereaboutsClient):
    signed_on: bool
    latest_activity_at: datetime


@dataclass(frozen=True, kw_only=True)
class Whereabouts:
    id: WhereaboutsID
    party: Party
    name: str
    description: str
    position: int
    hidden_if_empty: bool
    secret: bool


@dataclass(frozen=True, kw_only=True)
class WhereaboutsUserSound:
    user: User
    name: str


@dataclass(frozen=True, kw_only=True)
class WhereaboutsStatus:
    user: User
    whereabouts_id: WhereaboutsID
    set_at: datetime


@dataclass(frozen=True, kw_only=True)
class WhereaboutsUpdate:
    id: UUID
    user: User
    whereabouts_id: WhereaboutsID
    created_at: datetime
    source_address: IPAddress | None
