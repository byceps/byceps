"""
:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from uuid import UUID

import pytest

from byceps.services.user.dbmodels.avatar import DbUserAvatar
from byceps.typing import UserID
from byceps.util.image.models import ImageType


@pytest.mark.parametrize(
    'database_value, expected',
    [
        ('gif' , ImageType.gif ),
        ('jpeg', ImageType.jpeg),
        ('png' , ImageType.png ),
        ('webp', ImageType.webp),
    ],
)
def test_hybrid_image_type_getter(database_value, expected):
    avatar = create_avatar()

    avatar._image_type = database_value

    assert avatar.image_type == expected


@pytest.mark.parametrize(
    'image_type, expected',
    [
        (ImageType.gif , 'gif' ),
        (ImageType.jpeg, 'jpeg'),
        (ImageType.png , 'png' ),
        (ImageType.webp, 'webp'),
    ],
)
def test_hybrid_image_type_setter(image_type, expected):
    avatar = create_avatar()

    avatar.image_type = image_type

    assert avatar._image_type == expected


# helpers


def create_avatar() -> DbUserAvatar:
    creator_id = UserID(UUID('a96629ac-b17d-43d8-b93d-ec5a9fe9ba67'))
    return DbUserAvatar(creator_id, ImageType.jpeg)
