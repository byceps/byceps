"""
byceps.services.user.user_import_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from collections.abc import Iterator
from datetime import date
from io import TextIOBase
import json
import secrets
from typing import Optional

from pydantic import BaseModel, ValidationError

from . import user_creation_service
from .models.user import User


class UserToImport(BaseModel):
    screen_name: str
    # Use `Optional` instead of `| None` for pydantic on Python 3.9.
    email_address: Optional[str] = None  # noqa: UP007
    legacy_id: Optional[str] = None  # noqa: UP007
    first_name: Optional[str] = None  # noqa: UP007
    last_name: Optional[str] = None  # noqa: UP007
    date_of_birth: Optional[date] = None  # noqa: UP007
    country: Optional[str] = None  # noqa: UP007
    zip_code: Optional[str] = None  # noqa: UP007
    city: Optional[str] = None  # noqa: UP007
    street: Optional[str] = None  # noqa: UP007
    phone_number: Optional[str] = None  # noqa: UP007
    internal_comment: Optional[str] = None  # noqa: UP007


def parse_lines(lines: TextIOBase) -> Iterator[str]:
    for line in lines:
        yield line.strip()


def parse_user_json(json_data: str) -> UserToImport:
    data_dict = json.loads(json_data)

    try:
        return UserToImport.model_validate(data_dict)
    except ValidationError as exc:
        raise Exception(str(exc)) from exc


def import_user(user_to_import: UserToImport) -> User:
    password = secrets.token_urlsafe(24)

    user, _ = user_creation_service.create_user(
        user_to_import.screen_name,
        user_to_import.email_address,
        password,
        legacy_id=user_to_import.legacy_id,
        first_name=user_to_import.first_name,
        last_name=user_to_import.last_name,
        date_of_birth=user_to_import.date_of_birth,
        country=user_to_import.country,
        zip_code=user_to_import.zip_code,
        city=user_to_import.city,
        street=user_to_import.street,
        phone_number=user_to_import.phone_number,
        internal_comment=user_to_import.internal_comment,
        creation_method='import',
    ).unwrap()

    return user
