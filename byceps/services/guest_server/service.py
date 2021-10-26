"""
byceps.services.guest_server.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
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

from .dbmodels import Address as DbAddress, Server as DbServer
from .transfer.models import Address, AddressID, IPAddress, Server, ServerID


def create_server(
    party_id: PartyID,
    creator_id: UserID,
    owner_id: UserID,
    *,
    notes_owner: Optional[str] = None,
    hostname: Optional[str] = None,
) -> tuple[Server, GuestServerRegistered]:
    """Create a server."""
    party = party_service.get_party(party_id)
    creator = user_service.get_user(creator_id)
    owner = user_service.get_user(owner_id)

    db_server = DbServer(
        party.id, creator.id, owner.id, notes_owner=notes_owner
    )
    db.session.add(db_server)

    db_address = DbAddress(db_server, hostname=hostname)
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


def find_server(server_id: ServerID) -> Optional[Server]:
    """Return the server, if found."""
    db_server = db.session.execute(
        select(DbServer)
        .filter_by(id=server_id)
    ).scalars().one_or_none()

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


def _db_entity_to_server(db_server: DbServer) -> Server:
    addresses = {
        Address(
            id=db_address.id,
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
