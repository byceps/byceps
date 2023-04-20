"""
byceps.services.guest_server.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from ipaddress import IPv4Address, IPv6Address
from typing import NewType, Union
from uuid import UUID

from byceps.typing import PartyID, UserID


IPAddress = Union[IPv4Address, IPv6Address]


ServerID = NewType('ServerID', UUID)


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
    creator_id: UserID
    owner_id: UserID
    notes_owner: str | None
    notes_admin: str | None
    approved: bool
    addresses: set[Address]


@dataclass(frozen=True)
class Address:
    id: AddressID
    server_id: ServerID
    ip_address: IPAddress | None
    hostname: str | None
    netmask: IPAddress | None
    gateway: IPAddress | None
