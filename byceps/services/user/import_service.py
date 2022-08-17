"""
byceps.services.user.import_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import date
import json
from io import TextIOBase
import secrets
from typing import Iterator, Optional

from pydantic import BaseModel, ValidationError

from . import creation_service
from .transfer.models import User


class UserToImport(BaseModel):
    screen_name: str
    email_address: Optional[str] = None
    legacy_id: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    country: Optional[str] = None
    zip_code: Optional[str] = None
    city: Optional[str] = None
    street: Optional[str] = None
    phone_number: Optional[str] = None
    internal_comment: Optional[str] = None


def parse_lines(lines: TextIOBase) -> Iterator[str]:
    for line in lines:
        yield line.strip()


def parse_user_json(json_data: str) -> UserToImport:
    data_dict = json.loads(json_data)

    try:
        return UserToImport.parse_obj(data_dict)
    except ValidationError as e:
        raise Exception(str(e))


def import_user(user_to_import: UserToImport) -> User:
    password = secrets.token_urlsafe(24)

    user, _ = creation_service.create_user(
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
    )

    return user
