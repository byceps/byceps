"""
byceps.services.user.events
~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass

from byceps.services.core.events import _BaseEvent, EventSite
from byceps.services.user.models.user import User, UserAvatarID, UserID


@dataclass(frozen=True, kw_only=True)
class UserEvent(_BaseEvent):
    user: User


@dataclass(frozen=True, kw_only=True)
class UserAccountCreatedEvent(UserEvent):
    site: EventSite | None


@dataclass(frozen=True, kw_only=True)
class UserAccountDeletedEvent(UserEvent):
    reason: str


@dataclass(frozen=True, kw_only=True)
class UserAccountSuspendedEvent(UserEvent):
    reason: str


@dataclass(frozen=True, kw_only=True)
class UserAccountUnsuspendedEvent(UserEvent):
    reason: str


@dataclass(frozen=True, kw_only=True)
class UserAvatarEvent(UserEvent):
    avatar_id: UserAvatarID


@dataclass(frozen=True, kw_only=True)
class UserAvatarRemovedEvent(UserAvatarEvent):
    pass


@dataclass(frozen=True, kw_only=True)
class UserAvatarUpdatedEvent(UserAvatarEvent):
    pass


@dataclass(frozen=True, kw_only=True)
class UserDetailsUpdatedEvent(UserEvent):
    fields: dict[str, dict[str, str | None]]


@dataclass(frozen=True, kw_only=True)
class UserEmailAddressChangedEvent(UserEvent):
    pass


@dataclass(frozen=True, kw_only=True)
class UserEmailAddressConfirmedEvent(UserEvent):
    pass


@dataclass(frozen=True, kw_only=True)
class UserEmailAddressInvalidatedEvent(UserEvent):
    pass


@dataclass(frozen=True, kw_only=True)
class UserScreenNameChangedEvent(_BaseEvent):
    user_id: UserID
    old_screen_name: str | None
    new_screen_name: str | None
    reason: str | None
