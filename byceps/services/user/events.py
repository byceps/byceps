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
class _UserEvent(_BaseEvent):
    user: User


@dataclass(frozen=True, kw_only=True)
class UserAccountCreatedEvent(_UserEvent):
    site: EventSite | None


@dataclass(frozen=True, kw_only=True)
class UserAccountDeletedEvent(_UserEvent):
    reason: str


@dataclass(frozen=True, kw_only=True)
class UserAccountSuspendedEvent(_UserEvent):
    reason: str


@dataclass(frozen=True, kw_only=True)
class UserAccountUnsuspendedEvent(_UserEvent):
    reason: str


@dataclass(frozen=True, kw_only=True)
class _UserAvatarEvent(_UserEvent):
    avatar_id: UserAvatarID


@dataclass(frozen=True, kw_only=True)
class UserAvatarRemovedEvent(_UserAvatarEvent):
    pass


@dataclass(frozen=True, kw_only=True)
class UserAvatarUpdatedEvent(_UserAvatarEvent):
    pass


@dataclass(frozen=True, kw_only=True)
class UserDetailsUpdatedEvent(_UserEvent):
    pass


@dataclass(frozen=True, kw_only=True)
class UserEmailAddressChangedEvent(_UserEvent):
    pass


@dataclass(frozen=True, kw_only=True)
class UserEmailAddressConfirmedEvent(_UserEvent):
    pass


@dataclass(frozen=True, kw_only=True)
class UserEmailAddressInvalidatedEvent(_UserEvent):
    pass


@dataclass(frozen=True, kw_only=True)
class UserScreenNameChangedEvent(_BaseEvent):
    user_id: UserID
    old_screen_name: str | None
    new_screen_name: str | None
    reason: str | None
