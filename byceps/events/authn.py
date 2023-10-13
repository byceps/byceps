"""
byceps.events.authn
~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from dataclasses import dataclass

from byceps.services.site.models import SiteID
from byceps.services.user.models.user import UserID

from .base import _BaseEvent


@dataclass(frozen=True)
class PasswordUpdatedEvent(_BaseEvent):
    user_id: UserID
    user_screen_name: str | None


@dataclass(frozen=True)
class _UserIdentityTagEvent(_BaseEvent):
    identifier: str
    user_id: UserID
    user_screen_name: str | None


@dataclass(frozen=True)
class UserIdentityTagCreatedEvent(_UserIdentityTagEvent):
    pass


@dataclass(frozen=True)
class UserIdentityTagDeletedEvent(_UserIdentityTagEvent):
    pass


@dataclass(frozen=True)
class UserLoggedInEvent(_BaseEvent):
    site_id: SiteID | None
    site_title: str | None
