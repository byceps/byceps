"""
byceps.services.user.models.user
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum
from pathlib import Path
from typing import Any, NewType
from uuid import UUID

from secret_type import Secret

from byceps.util.image.image_type import ImageType


USER_DELETED_AVATAR_URL_PATH = '/static/user_avatar_deleted.svg'
USER_FALLBACK_AVATAR_URL_PATH = '/static/user_avatar_fallback.svg'


UserID = NewType('UserID', UUID)


UserAvatarID = NewType('UserAvatarID', UUID)


Password = Secret[str]


PasswordHash = Secret[str]


@dataclass(frozen=True, kw_only=True)
class UserAvatar:
    id: UserAvatarID
    created_at: datetime
    image_type: ImageType
    filename: Path
    path: Path
    url: str


@dataclass(frozen=True, kw_only=True)
class User:
    id: UserID
    screen_name: str | None
    initialized: bool
    suspended: bool
    deleted: bool
    avatar_url: str


@dataclass(frozen=True, kw_only=True)
class UserEmailAddress:
    address: str | None
    verified: bool


@dataclass(frozen=True, kw_only=True)
class UserDetail:
    first_name: str | None
    last_name: str | None
    date_of_birth: date | None
    country: str | None
    postal_code: str | None
    city: str | None
    street: str | None
    phone_number: str | None
    internal_comment: str | None
    extras: dict[str, Any]

    @property
    def full_name(self) -> str | None:
        names = [self.first_name, self.last_name]
        return ' '.join(filter(None, names)) or None


@dataclass(frozen=True, kw_only=True)
class UserDetailDifference:
    old: str | None
    new: str | None


@dataclass(frozen=True, kw_only=True)
class UserForAdmin(User):
    created_at: datetime
    detail: UserForAdminDetail


@dataclass(frozen=True, kw_only=True)
class UserForAdminDetail:
    full_name: str | None


UserFilter = Enum(
    'UserFilter',
    [
        'none',
        'active',
        'uninitialized',
        'suspended',
        'deleted',
    ],
)
