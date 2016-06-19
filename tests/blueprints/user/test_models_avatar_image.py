# -*- coding: utf-8 -*-

"""
:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime
from unittest import TestCase

from nose2.tools import params

from byceps.util.image import ImageType

from testfixtures.user import create_user


CREATED_AT = datetime(2014, 7, 29, 14, 43, 30, 196165)


class AvatarImageTestCase(TestCase):

    def setUp(self):
        self.user = create_user(1)

    @params(
        (None      , None          , False),
        (CREATED_AT, None          , False),
        (None      , ImageType.jpeg, False),
        (CREATED_AT, ImageType.jpeg, True ),
    )
    def test_has_avatar_image(self, created_at, image_type, expected):
        self.user.avatar_image_created_at = created_at
        self.user.avatar_image_type = image_type

        self.assertEqual(self.user.has_avatar_image, expected)

    @params(
        (None  , None          ),
        ('gif' , ImageType.gif ),
        ('jpeg', ImageType.jpeg),
        ('png' , ImageType.png ),
    )
    def test_hybrid_image_type_getter(self, database_value, expected):
        self.user._avatar_image_type = database_value

        self.assertEqual(self.user.avatar_image_type, expected)

    @params(
        (None          , None  ),
        (ImageType.gif , 'gif' ),
        (ImageType.jpeg, 'jpeg'),
        (ImageType.png , 'png' ),
    )
    def test_hybrid_image_type_setter(self, image_type, expected):
        self.user.avatar_image_type = image_type

        self.assertEqual(self.user._avatar_image_type, expected)
