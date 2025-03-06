"""
byceps.services.discord.discord_domain_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.util.uuid import generate_uuid7

from .models import (
    DiscordBotToken,
    DiscordClientSecret,
    DiscordGuildID,
    DiscordServer,
    DiscordServerID,
)


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
    server_id = DiscordServerID(generate_uuid7())

    return DiscordServer(
        id=server_id,
        name=name,
        guild_id=guild_id,
        invitation_url=invitation_url,
        bot_token=bot_token,
        client_id=client_id,
        client_secret=client_secret,
        enabled=enabled,
    )
