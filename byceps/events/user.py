"""
byceps.events.user
~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from dataclasses import dataclass

from byceps.services.user.models.user import UserID

from .base import _BaseEvent, EventSite, EventUser


@dataclass(frozen=True)
class _UserEvent(_BaseEvent):
    user: EventUser


@dataclass(frozen=True)
class UserAccountCreatedEvent(_UserEvent):
    site: EventSite | None


@dataclass(frozen=True)
class UserAccountDeletedEvent(_UserEvent):
    pass


@dataclass(frozen=True)
class UserAccountSuspendedEvent(_UserEvent):
    pass


@dataclass(frozen=True)
class UserAccountUnsuspendedEvent(_UserEvent):
    pass


@dataclass(frozen=True)
class UserDetailsUpdatedEvent(_UserEvent):
    pass


@dataclass(frozen=True)
class UserEmailAddressChangedEvent(_UserEvent):
    pass


@dataclass(frozen=True)
class UserEmailAddressConfirmedEvent(_UserEvent):
    pass


@dataclass(frozen=True)
class UserEmailAddressInvalidatedEvent(_UserEvent):
    pass


@dataclass(frozen=True)
class UserScreenNameChangedEvent(_BaseEvent):
    user_id: UserID
    old_screen_name: str | None
    new_screen_name: str | None
