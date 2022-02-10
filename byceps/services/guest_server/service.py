"""
byceps.services.guest_server.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from typing import Optional
from uuid import UUID

from sqlalchemy import delete, select

from ...database import db
from ...events.guest_server import GuestServerRegistered
from ...typing import PartyID, UserID

from ..party import service as party_service
from ..user import service as user_service

from .dbmodels import (
    Address as DbAddress,
    Server as DbServer,
    Setting as DbSetting,
)
from .transfer.models import (
    Address,
    AddressID,
    IPAddress,
    Server,
    ServerID,
    Setting,
)


# -------------------------------------------------------------------- #
# setting


def get_setting_for_party(party_id: PartyID) -> Setting:
    """Return the setting for the party."""
    db_setting = _get_db_setting(party_id)

    if db_setting is None:
        return Setting(
            party_id=party_id,
            netmask=None,
            gateway=None,
            dns_server1=None,
            dns_server2=None,
            domain=None,
        )

    return _db_entity_to_setting(db_setting)


def update_setting(
    party_id: PartyID,
    netmask: Optional[IPAddress],
    gateway: Optional[IPAddress],
    dns_server1: Optional[IPAddress],
    dns_server2: Optional[IPAddress],
    domain: Optional[str],
) -> Setting:
    """Update the setting for the party."""
    party = party_service.get_party(party_id)

    db_setting = _get_db_setting(party_id) or DbSetting(party_id)

    db_setting.netmask = netmask
    db_setting.gateway = gateway
    db_setting.dns_server1 = dns_server1
    db_setting.dns_server2 = dns_server2
    db_setting.domain = domain

    db.session.add(db_setting)
    db.session.commit()

    return _db_entity_to_setting(db_setting)


def _get_db_setting(party_id: PartyID) -> Optional[DbSetting]:
    return db.session.execute(
        select(DbSetting)
        .filter_by(party_id=party_id)
    ).scalar_one_or_none()


def _db_entity_to_setting(db_setting: DbSetting) -> Setting:
    return Setting(
        party_id=db_setting.party_id,
        netmask=db_setting.netmask,
        gateway=db_setting.gateway,
        dns_server1=db_setting.dns_server1,
        dns_server2=db_setting.dns_server2,
        domain=db_setting.domain,
    )


# -------------------------------------------------------------------- #
# server


def create_server(
    party_id: PartyID,
    creator_id: UserID,
    owner_id: UserID,
    *,
    notes_owner: Optional[str] = None,
    notes_admin: Optional[str] = None,
    approved: bool = False,
    ip_address: Optional[IPAddress] = None,
    hostname: Optional[str] = None,
) -> tuple[Server, GuestServerRegistered]:
    """Create a server."""
    party = party_service.get_party(party_id)
    creator = user_service.get_user(creator_id)
    owner = user_service.get_user(owner_id)

    db_server = DbServer(
        party.id,
        creator.id,
        owner.id,
        notes_owner=notes_owner,
        notes_admin=notes_admin,
        approved=approved,
    )
    db.session.add(db_server)

    db_address = DbAddress(db_server, ip_address=ip_address, hostname=hostname)
    db.session.add(db_address)

    db.session.commit()

    server = _db_entity_to_server(db_server)

    event = GuestServerRegistered(
        occurred_at=server.created_at,
        initiator_id=creator.id,
        initiator_screen_name=creator.screen_name,
        party_id=party.id,
        owner_id=owner.id,
        owner_screen_name=owner.screen_name,
        server_id=server.id,
    )

    return server, event


def update_server(
    server_id: ServerID,
    notes_admin: Optional[str],
    approved: bool,
) -> Server:
    """Update the server."""
    db_server = _get_db_server(server_id)

    db_server.notes_admin = notes_admin
    db_server.approved = approved

    db.session.commit()

    return _db_entity_to_server(db_server)


def find_server(server_id: ServerID) -> Optional[Server]:
    """Return the server, if found."""
    db_server = _find_db_server(server_id)

    if db_server is None:
        return None

    return _db_entity_to_server(db_server)


def get_all_servers_for_party(party_id: PartyID) -> list[Server]:
    """Return all servers for the party."""
    db_servers = db.session.execute(
        select(DbServer)
        .filter_by(party_id=party_id)
        .join(DbAddress)
    ).scalars().unique().all()

    return [_db_entity_to_server(db_server) for db_server in db_servers]


def get_servers_for_owner_and_party(
    owner_id: UserID, party_id: PartyID
) -> list[Server]:
    """Return the servers owned by the user for the party."""
    db_servers = db.session.execute(
        select(DbServer)
        .filter_by(owner_id=owner_id)
        .filter_by(party_id=party_id)
        .join(DbAddress)
    ).scalars().unique().all()

    return [_db_entity_to_server(db_server) for db_server in db_servers]


def count_servers_for_owner_and_party(
    owner_id: UserID, party_id: PartyID
) -> int:
    """Return the number of servers owned by the user for the party."""
    return db.session.scalar(
        select(db.func.count(DbServer.id))
        .filter_by(owner_id=owner_id)
        .filter_by(party_id=party_id)
    )


def delete_server(server_id: ServerID) -> None:
    """Delete a server and its addresses."""
    db.session.execute(
        delete(DbAddress)
        .where(DbAddress.server_id == server_id)
        .execution_options(synchronize_session='fetch')
    )

    db.session.execute(
        delete(DbServer)
        .where(DbServer.id == server_id)
        .execution_options(synchronize_session='fetch')
    )

    db.session.commit()


def _find_db_server(server_id: ServerID) -> Optional[DbServer]:
    return db.session.execute(
        select(DbServer)
        .filter_by(id=server_id)
    ).scalars().one_or_none()


def _get_db_server(server_id: ServerID) -> DbServer:
    db_server = _find_db_server(server_id)

    if db_server is None:
        raise ValueError(f'Unknown server ID "{server_id}"')

    return db_server


def _db_entity_to_server(db_server: DbServer) -> Server:
    addresses = {
        Address(
            id=db_address.id,
            server_id=db_server.id,
            ip_address=db_address.ip_address,
            hostname=db_address.hostname,
        )
        for db_address in db_server.addresses
    }

    return Server(
        id=db_server.id,
        party_id=db_server.party_id,
        created_at=db_server.created_at,
        creator_id=db_server.creator_id,
        owner_id=db_server.owner_id,
        notes_owner=db_server.notes_owner,
        notes_admin=db_server.notes_admin,
        approved=db_server.approved,
        addresses=addresses,
    )


# -------------------------------------------------------------------- #
# address


def find_address(address_id: AddressID) -> Optional[Address]:
    """Return the address, if found."""
    db_address = _find_db_address(address_id)

    if db_address is None:
        return None

    return _db_entity_to_address(db_address)


def create_address(
    server_id: ServerID,
    ip_address: Optional[IPAddress] = None,
    hostname: Optional[str] = None,
) -> Address:
    """Append an address to a server."""
    db_server = _get_db_server(server_id)

    db_address = DbAddress(db_server, ip_address=ip_address, hostname=hostname)
    db.session.add(db_address)

    db.session.commit()

    return _db_entity_to_address(db_address)


def update_address(
    address_id: AddressID,
    ip_address: Optional[IPAddress],
    hostname: Optional[str],
) -> Address:
    """Update the address."""
    db_address = _find_db_address(address_id)

    if db_address is None:
        raise ValueError(f'Unknown address ID "{address_id}"')

    db_address.ip_address = ip_address
    db_address.hostname = hostname

    db.session.commit()

    return _db_entity_to_address(db_address)


def _find_db_address(address_id: AddressID) -> Optional[DbAddress]:
    return db.session.execute(
        select(DbAddress)
        .filter_by(id=address_id)
    ).scalars().one_or_none()


def _db_entity_to_address(db_address: DbAddress) -> Address:
    return Address(
        id=db_address.id,
        server_id=db_address.server_id,
        ip_address=db_address.ip_address,
        hostname=db_address.hostname,
    )
