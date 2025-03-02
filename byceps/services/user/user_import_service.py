"""
byceps.services.user.user_import_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections.abc import Iterator
from datetime import date
from io import TextIOBase
import json
import secrets

from pydantic import BaseModel, ValidationError
from secret_type import secret

from . import user_creation_service
from .models.user import User


class UserToImport(BaseModel):
    screen_name: str
    email_address: str | None = None
    legacy_id: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    date_of_birth: date | None = None
    country: str | None = None
    zip_code: str | None = None
    city: str | None = None
    street: str | None = None
    phone_number: str | None = None
    internal_comment: str | None = None


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
    password = secret(secrets.token_urlsafe(24))

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
