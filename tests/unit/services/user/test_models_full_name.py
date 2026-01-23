"""
:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

import pytest

from byceps.services.user.dbmodels import DbUser, DbUserDetail
from byceps.services.user.models.user import UserID
from byceps.util.uuid import generate_uuid4


@pytest.mark.parametrize(
    ('first_name', 'last_name', 'expected'),
    [
        (None, None, None),
        ('Giesbert Z.', None, 'Giesbert Z.'),
        (None, 'Blümli', 'Blümli'),
        ('Giesbert Z.', 'Blümli', 'Giesbert Z. Blümli'),
    ],
)
def test_full_name(first_name, last_name, expected):
    user = create_user(first_name, last_name)

    assert user.detail.full_name == expected


def create_user(first_name: str, last_name: str) -> DbUser:
    user_id = UserID(generate_uuid4())
    created_at = datetime.utcnow()
    screen_name = 'Anyone'
    email_address = 'anyone@example.test'

    user = DbUser(user_id, created_at, screen_name, email_address)

    detail = DbUserDetail(user=user)
    detail.first_name = first_name
    detail.last_name = last_name

    return user
