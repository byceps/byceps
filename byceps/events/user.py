"""
byceps.events.user
~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from dataclasses import dataclass
from typing import Optional

from ..typing import UserID

from .base import _BaseEvent


@dataclass(frozen=True)
class _UserEvent(_BaseEvent):
    user_id: UserID


@dataclass(frozen=True)
class UserAccountCreated(_UserEvent):
    user_screen_name: str


@dataclass(frozen=True)
class UserAccountDeleted(_UserEvent):
    user_screen_name: Optional[str]


@dataclass(frozen=True)
class UserAccountSuspended(_UserEvent):
    pass


@dataclass(frozen=True)
class UserAccountUnsuspended(_UserEvent):
    pass


@dataclass(frozen=True)
class UserDetailsUpdated(_UserEvent):
    pass


@dataclass(frozen=True)
class UserEmailAddressChanged(_UserEvent):
    pass


@dataclass(frozen=True)
class UserEmailAddressConfirmed(_UserEvent):
    pass


@dataclass(frozen=True)
class UserEmailAddressInvalidated(_UserEvent):
    pass


@dataclass(frozen=True)
class UserScreenNameChanged(_UserEvent):
    old_screen_name: str
    new_screen_name: str
