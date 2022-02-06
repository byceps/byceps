"""
byceps.services.user.import_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
import json
from io import TextIOBase
import secrets
from typing import Iterator

from marshmallow import fields, Schema, ValidationError

from . import creation_service
from .transfer.models import User


class UserImportSchema(Schema):
    screen_name = fields.Str(required=True)
    email_address = fields.Str(required=False)
    legacy_id = fields.Str(required=False)
    first_name = fields.Str(required=False)
    last_name = fields.Str(required=False)
    date_of_birth = fields.Date(required=False)
    country = fields.Str(required=False)
    zip_code = fields.Str(required=False)
    city = fields.Str(required=False)
    street = fields.Str(required=False)
    phone_number = fields.Str(required=False)
    internal_comment = fields.Str(required=False)


def parse_lines(lines: TextIOBase) -> Iterator[str]:
    for line in lines:
        yield line.strip()


def parse_user_json(json_data: str) -> dict[str, str]:
    data_dict = json.loads(json_data)

    schema = UserImportSchema()
    try:
        return schema.load(data_dict)
    except ValidationError as e:
        raise Exception(str(e.normalized_messages()))


def create_user(user_dict) -> User:
    password = secrets.token_urlsafe(24)

    user, _ = creation_service.create_user(
        user_dict['screen_name'],
        user_dict.get('email_address'),
        password,
        legacy_id=user_dict.get('legacy_id'),
        first_name=user_dict.get('first_name'),
        last_name=user_dict.get('last_name'),
        date_of_birth=user_dict.get('date_of_birth'),
        country=user_dict.get('country'),
        zip_code=user_dict.get('zip_code'),
        city=user_dict.get('city'),
        street=user_dict.get('street'),
        phone_number=user_dict.get('phone_number'),
        internal_comment=user_dict.get('internal_comment'),
    )

    return user
