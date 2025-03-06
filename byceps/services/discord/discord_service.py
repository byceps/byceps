"""
byceps.services.discord.discord_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from secret_type import secret
from sqlalchemy import select

from byceps.database import db

from . import discord_domain_service
from .dbmodels import DbDiscordServer
from .models import (
    DiscordBotToken,
    DiscordClientSecret,
    DiscordGuildID,
    DiscordServer,
    DiscordServerID,
)


# -------------------------------------------------------------------- #
# server


def create_server(
    name: str,
    guild_id: DiscordGuildID,
    enabled: bool,
    *,
    invitation_url: str | None = None,
    bot_token: DiscordBotToken | None = None,
    client_id: str | None = None,
    client_secret: DiscordClientSecret | None = None,
) -> DiscordServer:
    """Create a server."""
    server = discord_domain_service.create_server(
        name,
        guild_id,
        enabled,
        invitation_url=invitation_url,
        bot_token=bot_token,
        client_id=client_id,
        client_secret=client_secret,
    )

    _persist_server_creation(server)

    return server


def _persist_server_creation(server: DiscordServer) -> None:
    db_server = DbDiscordServer(
        server.id,
        server.name,
        server.guild_id,
        server.enabled,
        invitation_url=server.invitation_url,
        bot_token=server.bot_token,
        client_id=server.client_id,
        client_secret=server.client_secret,
    )
    db.session.add(db_server)
    db.session.commit()


def find_server(server_id: DiscordServerID) -> DiscordServer | None:
    """Return the server."""
    db_server = _find_db_server(server_id)

    if db_server is None:
        return None

    return _db_entity_to_server(db_server)


def _find_db_server(server_id: DiscordServerID) -> DbDiscordServer | None:
    """Return the server, if found."""
    return db.session.get(DbDiscordServer, server_id)


def get_servers() -> list[DiscordServer]:
    """Return all servers."""
    db_servers = db.session.scalars(select(DbDiscordServer)).all()

    return [_db_entity_to_server(db_server) for db_server in db_servers]


def _db_entity_to_server(db_server: DbDiscordServer) -> DiscordServer:
    return DiscordServer(
        id=db_server.id,
        name=db_server.name,
        guild_id=db_server.guild_id,
        invitation_url=db_server.invitation_url,
        bot_token=secret(db_server.bot_token)
        if db_server.bot_token is not None
        else None,
        client_id=db_server.client_id,
        client_secret=secret(db_server.client_secret)
        if db_server.client_secret is not None
        else None,
        enabled=db_server.enabled,
    )
