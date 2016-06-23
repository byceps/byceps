# -*- coding: utf-8 -*-

"""
:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from nose2.tools import params

from byceps.util.image import ImageType

from testfixtures.user import create_user


@params(
    (None  , None          ),
    ('gif' , ImageType.gif ),
    ('jpeg', ImageType.jpeg),
    ('png' , ImageType.png ),
)
def test_hybrid_image_type_getter(database_value, expected):
    user = create_user(1)

    user._avatar_image_type = database_value

    assert user.avatar_image_type == expected


@params(
    (None          , None  ),
    (ImageType.gif , 'gif' ),
    (ImageType.jpeg, 'jpeg'),
    (ImageType.png , 'png' ),
)
def test_hybrid_image_type_setter(image_type, expected):
    user = create_user(1)

    user.avatar_image_type = image_type

    assert user._avatar_image_type == expected
