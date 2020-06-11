"""
byceps.services.user.transfer.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from dataclasses import dataclass
from datetime import date
from typing import Any, Dict, Optional

from ....typing import UserID


@dataclass(frozen=True)
class User:
    id: UserID
    screen_name: Optional[str]
    suspended: bool
    deleted: bool
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
    extras: Dict[str, Any]


@dataclass(frozen=True)
class UserWithDetail(User):
    detail: UserDetail
