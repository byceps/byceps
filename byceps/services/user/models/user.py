"""
byceps.services.user.models.user
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum
from typing import Any, NewType
from uuid import UUID

from byceps.typing import UserID


UserAvatarID = NewType('UserAvatarID', UUID)


@dataclass(frozen=True)
class User:
    id: UserID
    screen_name: str | None
    suspended: bool
    deleted: bool
    locale: str | None
    avatar_url: str | None


@dataclass(frozen=True)
class UserEmailAddress:
    address: str | None
    verified: bool


@dataclass(frozen=True)
class UserDetail:
    first_name: str | None
    last_name: str | None
    date_of_birth: date | None
    country: str | None
    zip_code: str | None
    city: str | None
    street: str | None
    phone_number: str | None
    internal_comment: str | None
    extras: dict[str, Any]

    @property
    def full_name(self) -> str | None:
        names = [self.first_name, self.last_name]
        return ' '.join(filter(None, names)) or None


@dataclass(frozen=True)
class UserForAdmin(User):
    created_at: datetime
    initialized: bool
    detail: UserForAdminDetail


@dataclass(frozen=True)
class UserForAdminDetail:
    full_name: str | None


UserStateFilter = Enum(
    'UserStateFilter',
    [
        'none',
        'active',
        'uninitialized',
        'suspended',
        'deleted',
    ],
)
