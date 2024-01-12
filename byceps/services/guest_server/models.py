"""
byceps.services.guest_server.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2024 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from ipaddress import IPv4Address, IPv6Address
from typing import NewType
from uuid import UUID

from byceps.services.party.models import PartyID
from byceps.services.user.models.user import User


IPAddress = IPv4Address | IPv6Address


ServerID = NewType('ServerID', UUID)


ServerStatus = Enum(
    'ServerStatus', ['pending', 'approved', 'checked_in', 'checked_out']
)


AddressID = NewType('AddressID', UUID)


@dataclass(frozen=True)
class Setting:
    party_id: PartyID
    netmask: IPAddress | None
    gateway: IPAddress | None
    dns_server1: IPAddress | None
    dns_server2: IPAddress | None
    domain: str | None


@dataclass(frozen=True)
class Server:
    id: ServerID
    party_id: PartyID
    created_at: datetime
    creator: User
    owner: User
    description: str | None
    notes_owner: str | None
    notes_admin: str | None
    approved: bool
    checked_in: bool
    checked_in_at: datetime | None
    checked_out: bool
    checked_out_at: datetime | None
    addresses: set[Address]

    @property
    def status(self) -> ServerStatus:
        if self.checked_out:
            return ServerStatus.checked_out
        elif self.checked_in:
            return ServerStatus.checked_in
        elif self.approved:
            return ServerStatus.approved
        else:
            return ServerStatus.pending


@dataclass(frozen=True)
class ServerQuantitiesByStatus:
    pending: int
    approved: int
    checked_in: int
    checked_out: int
    total: int


@dataclass(frozen=True)
class Address:
    id: AddressID
    server_id: ServerID
    created_at: datetime
    ip_address: IPAddress | None
    hostname: str | None
    netmask: IPAddress | None
    gateway: IPAddress | None


@dataclass(frozen=True)
class AddressData:
    ip_address: IPAddress | None
    hostname: str | None
    netmask: IPAddress | None
    gateway: IPAddress | None
