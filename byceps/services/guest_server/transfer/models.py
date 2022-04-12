"""
byceps.services.guest_server.transfer.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from ipaddress import IPv4Address, IPv6Address
from typing import NewType, Optional, Union
from uuid import UUID

from ....typing import PartyID, UserID


IPAddress = Union[IPv4Address, IPv6Address]


ServerID = NewType('ServerID', UUID)


AddressID = NewType('AddressID', UUID)


@dataclass(frozen=True)
class Setting:
    party_id: PartyID
    netmask: Optional[IPAddress]
    gateway: Optional[IPAddress]
    dns_server1: Optional[IPAddress]
    dns_server2: Optional[IPAddress]
    domain: Optional[str]


@dataclass(frozen=True)
class Server:
    id: ServerID
    party_id: PartyID
    created_at: datetime
    creator_id: UserID
    owner_id: UserID
    notes_owner: Optional[str]
    notes_admin: Optional[str]
    approved: bool
    addresses: set[Address]


@dataclass(frozen=True)
class Address:
    id: AddressID
    server_id: ServerID
    ip_address: Optional[IPAddress]
    hostname: Optional[str]
    netmask: Optional[IPAddress]
    gateway: Optional[IPAddress]
