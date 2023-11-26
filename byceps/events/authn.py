"""
byceps.events.authn
~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from dataclasses import dataclass

from byceps.events.base import EventSite, EventUser

from .base import _BaseEvent


@dataclass(frozen=True)
class PasswordUpdatedEvent(_BaseEvent):
    user: EventUser


@dataclass(frozen=True)
class _UserIdentityTagEvent(_BaseEvent):
    identifier: str
    user: EventUser


@dataclass(frozen=True)
class UserIdentityTagCreatedEvent(_UserIdentityTagEvent):
    pass


@dataclass(frozen=True)
class UserIdentityTagDeletedEvent(_UserIdentityTagEvent):
    pass


@dataclass(frozen=True)
class UserLoggedInEvent(_BaseEvent):
    site: EventSite | None
