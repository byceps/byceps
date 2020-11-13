"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.services.user_avatar.models import Avatar
from byceps.util.image.models import ImageType

from testfixtures.user import create_user


@pytest.mark.parametrize(
    'database_value, expected',
    [
        (None  , None          ),
        ('gif' , ImageType.gif ),
        ('jpeg', ImageType.jpeg),
        ('png' , ImageType.png ),
    ],
)
def test_hybrid_image_type_getter(database_value, expected):
    user = create_user()
    avatar = create_avatar(user.id)

    avatar._image_type = database_value

    assert avatar.image_type == expected


@pytest.mark.parametrize(
    'image_type, expected',
    [
        (None          , None  ),
        (ImageType.gif , 'gif' ),
        (ImageType.jpeg, 'jpeg'),
        (ImageType.png , 'png' ),
    ],
)
def test_hybrid_image_type_setter(image_type, expected):
    user = create_user()
    avatar = create_avatar(user.id)

    avatar.image_type = image_type

    assert avatar._image_type == expected


# helpers


def create_avatar(creator_id):
    return Avatar(creator_id, ImageType.jpeg)
