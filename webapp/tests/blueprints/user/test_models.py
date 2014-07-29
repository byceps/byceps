# -*- coding: utf-8 -*-

from datetime import datetime
from unittest import TestCase

from nose2.tools import params

from byceps.blueprints.user.models import User
from byceps.util.image import ImageType


NOW = datetime.now()


class AvatarImageTestCase(TestCase):

    def setUp(self):
        self.user = User()

    @params(
        (None, None          , False),
        (NOW , None          , False),
        (None, ImageType.jpeg, False),
        (NOW , ImageType.jpeg, True ),
    )
    def test_has_avatar_image(self, created_at, image_type, expected):
        self.user.avatar_image_created_at = created_at
        self.user.avatar_image_type = image_type

        self.assertEquals(self.user.has_avatar_image, expected)

    @params(
        (None  , None          ),
        ('gif' , ImageType.gif ),
        ('jpeg', ImageType.jpeg),
        ('png' , ImageType.png ),
    )
    def test_get_avatar_image_type(self, database_value, expected):
        self.user._avatar_image_type = database_value

        self.assertEquals(self.user.avatar_image_type, expected)

    @params(
        (None          , None  ),
        (ImageType.gif , 'gif' ),
        (ImageType.jpeg, 'jpeg'),
        (ImageType.png , 'png' ),
    )
    def test_set_avatar_image_type(self, image_type, expected):
        self.user.avatar_image_type = image_type

        self.assertEquals(self.user._avatar_image_type, expected)
