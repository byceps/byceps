"""
:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

import pytest

from byceps.services.user.dbmodels import DbUserAvatar
from byceps.services.user.models import UserAvatarID
from byceps.util.image.image_type import ImageType

from tests.helpers import generate_uuid


@pytest.mark.parametrize(
    ('database_value', 'expected'),
    [
        ('gif', ImageType.gif),
        ('jpeg', ImageType.jpeg),
        ('png', ImageType.png),
        ('webp', ImageType.webp),
    ],
)
def test_hybrid_image_type_getter(database_value, expected):
    avatar = create_avatar()

    avatar._image_type = database_value

    assert avatar.image_type == expected


@pytest.mark.parametrize(
    ('image_type', 'expected'),
    [
        (ImageType.gif, 'gif'),
        (ImageType.jpeg, 'jpeg'),
        (ImageType.png, 'png'),
        (ImageType.webp, 'webp'),
    ],
)
def test_hybrid_image_type_setter(image_type, expected):
    avatar = create_avatar()

    avatar.image_type = image_type

    assert avatar._image_type == expected


# helpers


def create_avatar() -> DbUserAvatar:
    avatar_id = UserAvatarID(generate_uuid())
    created_at = datetime.utcnow()

    return DbUserAvatar(avatar_id, created_at, ImageType.jpeg)
