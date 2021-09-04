"""
byceps.events.user
~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from typing import Optional

from ..services.site.transfer.models import SiteID
from ..typing import UserID

from .base import _BaseEvent


@dataclass(frozen=True)
class _UserEvent(_BaseEvent):
    user_id: UserID


@dataclass(frozen=True)
class UserAccountCreated(_UserEvent):
    user_screen_name: Optional[str]
    site_id: Optional[SiteID]


@dataclass(frozen=True)
class UserAccountDeleted(_UserEvent):
    user_screen_name: Optional[str]


@dataclass(frozen=True)
class UserAccountSuspended(_UserEvent):
    user_screen_name: Optional[str]


@dataclass(frozen=True)
class UserAccountUnsuspended(_UserEvent):
    user_screen_name: Optional[str]


@dataclass(frozen=True)
class UserDetailsUpdated(_UserEvent):
    user_screen_name: Optional[str]


@dataclass(frozen=True)
class UserEmailAddressChanged(_UserEvent):
    user_screen_name: Optional[str]


@dataclass(frozen=True)
class UserEmailAddressConfirmed(_UserEvent):
    user_screen_name: Optional[str]


@dataclass(frozen=True)
class UserEmailAddressInvalidated(_UserEvent):
    user_screen_name: Optional[str]


@dataclass(frozen=True)
class UserScreenNameChanged(_UserEvent):
    old_screen_name: Optional[str]
    new_screen_name: Optional[str]
