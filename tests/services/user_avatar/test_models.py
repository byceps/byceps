"""
:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime

from nose2.tools import params

from byceps.util.image.models import ImageType

from testfixtures.user import create_user
from testfixtures.user_avatar import create_avatar


CREATED_AT = datetime(2014, 7, 29, 14, 43, 30, 196165)


@params(
    (None  , None          ),
    ('gif' , ImageType.gif ),
    ('jpeg', ImageType.jpeg),
    ('png' , ImageType.png ),
)
def test_hybrid_image_type_getter(database_value, expected):
    user = create_user()
    avatar = create_avatar(user.id)

    avatar._image_type = database_value

    assert avatar.image_type == expected


@params(
    (None          , None  ),
    (ImageType.gif , 'gif' ),
    (ImageType.jpeg, 'jpeg'),
    (ImageType.png , 'png' ),
)
def test_hybrid_image_type_setter(image_type, expected):
    user = create_user()
    avatar = create_avatar(user.id)

    avatar.image_type = image_type

    assert avatar._image_type == expected
