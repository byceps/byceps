"""
byceps.services.discord.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from datetime import datetime
from typing import NewType
from uuid import UUID

from secret_type import Secret


DiscordBotToken = Secret[str]


DiscordClientSecret = Secret[str]


DiscordGuildID = NewType('DiscordGuildID', str)


DiscordServerID = NewType('DiscordServerID', UUID)


@dataclass(frozen=True, kw_only=True)
class DiscordServer:
    id: DiscordServerID
    name: str
    guild_id: DiscordGuildID
    invitation_url: str | None
    bot_token: DiscordBotToken | None
    client_id: str | None
    client_secret: DiscordClientSecret | None
    enabled: bool


@dataclass(frozen=True, kw_only=True)
class DiscordServerPresenceStats:
    server_id: DiscordServerID
    updated_at: datetime
    member_count: int
    presence_count: int
