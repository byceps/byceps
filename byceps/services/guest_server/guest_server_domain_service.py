"""
byceps.services.guest_server.guest_server_domain_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from datetime import datetime

from byceps.database import generate_uuid7
from byceps.events.guest_server import GuestServerRegisteredEvent
from byceps.services.party.models import Party
from byceps.services.user.models.user import User

from .models import (
    Address,
    AddressID,
    IPAddress,
    Server,
    ServerID,
)


def create_server(
    party: Party,
    creator: User,
    owner: User,
    *,
    notes_owner: str | None = None,
    notes_admin: str | None = None,
    approved: bool = False,
    ip_address: IPAddress | None = None,
    hostname: str | None = None,
    netmask: IPAddress | None = None,
    gateway: IPAddress | None = None,
) -> tuple[Server, GuestServerRegisteredEvent]:
    """Create a server."""
    server_id = ServerID(generate_uuid7())
    occurred_at = datetime.utcnow()
    address = _build_address(
        server_id,
        occurred_at,
        ip_address=ip_address,
        hostname=hostname,
        netmask=netmask,
        gateway=gateway,
    )
    addresses = {address}

    server = _build_server(
        server_id,
        party,
        occurred_at,
        creator,
        owner,
        notes_owner,
        notes_admin,
        approved,
        addresses,
    )

    event = _build_guest_server_registered_event(server, party, creator, owner)

    return server, event


def _build_address(
    server_id: ServerID,
    created_at: datetime,
    *,
    ip_address: IPAddress | None = None,
    hostname: str | None = None,
    netmask: IPAddress | None = None,
    gateway: IPAddress | None = None,
) -> Address:
    return Address(
        id=AddressID(generate_uuid7()),
        created_at=created_at,
        server_id=server_id,
        ip_address=ip_address,
        hostname=hostname,
        netmask=netmask,
        gateway=gateway,
    )


def _build_server(
    server_id: ServerID,
    party: Party,
    created_at: datetime,
    creator: User,
    owner: User,
    notes_owner: str | None,
    notes_admin: str | None,
    approved: bool,
    addresses: set[Address],
) -> Server:
    return Server(
        id=server_id,
        party_id=party.id,
        created_at=created_at,
        creator_id=creator.id,
        owner_id=owner.id,
        notes_owner=notes_owner,
        notes_admin=notes_admin,
        approved=approved,
        addresses=addresses,
    )


def _build_guest_server_registered_event(
    server: Server, party: Party, creator: User, owner: User
) -> GuestServerRegisteredEvent:
    return GuestServerRegisteredEvent(
        occurred_at=server.created_at,
        initiator_id=creator.id,
        initiator_screen_name=creator.screen_name,
        party_id=party.id,
        party_title=party.title,
        owner_id=owner.id,
        owner_screen_name=owner.screen_name,
        server_id=server.id,
    )
