"""
byceps.events.user
~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from dataclasses import dataclass

from byceps.services.site.models import SiteID
from byceps.typing import UserID

from .base import _BaseEvent


@dataclass(frozen=True)
class _UserEvent(_BaseEvent):
    user_id: UserID


@dataclass(frozen=True)
class UserAccountCreatedEvent(_UserEvent):
    user_screen_name: str | None
    site_id: SiteID | None


@dataclass(frozen=True)
class UserAccountDeletedEvent(_UserEvent):
    user_screen_name: str | None


@dataclass(frozen=True)
class UserAccountSuspendedEvent(_UserEvent):
    user_screen_name: str | None


@dataclass(frozen=True)
class UserAccountUnsuspendedEvent(_UserEvent):
    user_screen_name: str | None


@dataclass(frozen=True)
class UserDetailsUpdatedEvent(_UserEvent):
    user_screen_name: str | None


@dataclass(frozen=True)
class UserEmailAddressChangedEvent(_UserEvent):
    user_screen_name: str | None


@dataclass(frozen=True)
class UserEmailAddressConfirmedEvent(_UserEvent):
    user_screen_name: str | None


@dataclass(frozen=True)
class UserEmailAddressInvalidatedEvent(_UserEvent):
    user_screen_name: str | None


@dataclass(frozen=True)
class UserScreenNameChangedEvent(_UserEvent):
    old_screen_name: str | None
    new_screen_name: str | None
