# -*- coding: utf-8 -*-

from datetime import datetime
from pathlib import Path
from unittest import TestCase
from uuid import UUID

from freezegun import freeze_time
from nose2.tools import params
from pytz import timezone

from byceps.blueprints.user.models import User
from byceps.util.image import ImageType

from tests import AbstractAppTestCase


CREATED_AT = datetime(2014, 7, 29, 14, 43, 30, 196165)

TIMEZONE = timezone('Europe/Berlin')


class AvatarImageTestCase(TestCase):

    def setUp(self):
        self.user = User()

    @params(
        (None      , None          , False),
        (CREATED_AT, None          , False),
        (None      , ImageType.jpeg, False),
        (CREATED_AT, ImageType.jpeg, True ),
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
    def test_hybrid_image_type_getter(self, database_value, expected):
        self.user._avatar_image_type = database_value

        self.assertEquals(self.user.avatar_image_type, expected)

    @params(
        (None          , None  ),
        (ImageType.gif , 'gif' ),
        (ImageType.jpeg, 'jpeg'),
        (ImageType.png , 'png' ),
    )
    def test_hybrid_image_type_setter(self, image_type, expected):
        self.user.avatar_image_type = image_type

        self.assertEquals(self.user._avatar_image_type, expected)


class AvatarImagePathTestCase(AbstractAppTestCase):

    def setUp(self):
        super().setUp()

        user_id = UUID('2e17cb15-d763-4f93-882a-371296a3c63f')
        self.user = User(id=user_id)

    def test_path(self):
        expected = Path(
            '/var/data/avatars/2e17cb15-d763-4f93-882a-371296a3c63f_1406637810.jpeg')

        with freeze_time('2014-07-29 14:43:30'):
            created_at = TIMEZONE.localize(datetime.now())

        self.user.set_avatar_image(created_at, ImageType.jpeg)

        with self.app.app_context():
            self.app.config['PATH_USER_AVATAR_IMAGES'] = Path('/var/data/avatars')
            self.assertEquals(self.user.avatar_image_path, expected)
