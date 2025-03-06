"""
byceps.services.discord.dbmodels
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from sqlalchemy.orm import Mapped, mapped_column

from byceps.database import db

from .models import (
    DiscordBotToken,
    DiscordClientSecret,
    DiscordGuildID,
    DiscordServerID,
)


class DbDiscordServer(db.Model):
    """A Discord server."""

    __tablename__ = 'discord_servers'

    id: Mapped[DiscordServerID] = mapped_column(db.Uuid, primary_key=True)
    name: Mapped[str] = mapped_column(db.UnicodeText)
    guild_id: Mapped[DiscordGuildID] = mapped_column(db.UnicodeText)
    invitation_url: Mapped[str | None] = mapped_column(db.UnicodeText)
    bot_token: Mapped[str | None] = mapped_column(db.UnicodeText)
    client_id: Mapped[str | None] = mapped_column(db.UnicodeText)
    client_secret: Mapped[str | None] = mapped_column(db.UnicodeText)
    enabled: Mapped[bool]

    def __init__(
        self,
        server_id: DiscordServerID,
        name: str,
        guild_id: DiscordGuildID,
        enabled: bool,
        *,
        invitation_url: str | None = None,
        bot_token: DiscordBotToken | None = None,
        client_id: str | None = None,
        client_secret: DiscordClientSecret | None = None,
    ) -> None:
        self.id = server_id
        self.name = name
        self.guild_id = guild_id
        self.invitation_url = invitation_url

        if bot_token is not None:
            with bot_token.dangerous_reveal() as bot_token:
                self.bot_token = bot_token
        else:
            self.bot_token = None

        self.client_id = client_id

        if client_secret is not None:
            with client_secret.dangerous_reveal() as client_secret:
                self.client_secret = client_secret
        else:
            self.client_secret = None

        self.enabled = enabled
