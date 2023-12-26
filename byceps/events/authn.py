"""
byceps.events.authn
~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass

from .base import _BaseEvent, EventSite, EventUser


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
