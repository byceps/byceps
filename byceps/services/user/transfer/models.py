"""
byceps.services.user.transfer.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from dataclasses import dataclass
from datetime import date
from typing import Any, Optional

from ....typing import UserID


@dataclass(frozen=True)
class User:
    id: UserID
    screen_name: Optional[str]
    suspended: bool
    deleted: bool
    locale: Optional[str]
    avatar_url: Optional[str]
    is_orga: bool


@dataclass(frozen=True)
class UserDetail:
    first_names: Optional[str]
    last_name: Optional[str]
    date_of_birth: Optional[date]
    country: Optional[str]
    zip_code: Optional[str]
    city: Optional[str]
    street: Optional[str]
    phone_number: Optional[str]
    internal_comment: Optional[str]
    extras: dict[str, Any]


@dataclass(frozen=True)
class UserWithDetail(User):
    detail: UserDetail
