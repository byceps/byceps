"""
byceps.services.user.import_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
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
    first_names = fields.Str(required=False)
    last_name = fields.Str(required=False)


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
        first_names=user_dict.get('first_names'),
        last_name=user_dict.get('last_name'),
    )

    return user
