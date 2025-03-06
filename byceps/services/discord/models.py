"""
byceps.services.discord.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from typing import NewType
from uuid import UUID

from secret_type import Secret


DiscordBotToken = Secret[str]


DiscordClientSecret = Secret[str]


DiscordGuildID = NewType('DiscordGuildID', str)


DiscordServerID = NewType('DiscordServerID', UUID)


@dataclass(frozen=True)
class DiscordServer:
    id: DiscordServerID
    name: str
    guild_id: DiscordGuildID
    invitation_url: str | None
    bot_token: DiscordBotToken | None
    client_id: str | None
    client_secret: DiscordClientSecret | None
    enabled: bool
