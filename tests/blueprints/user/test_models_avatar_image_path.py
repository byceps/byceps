# -*- coding: utf-8 -*-

"""
:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime
from pathlib import Path
from uuid import UUID

from freezegun import freeze_time
from pytz import timezone

from byceps.util.image import ImageType

from tests.base import AbstractAppTestCase

from testfixtures.user import create_user


TIMEZONE = timezone('Europe/Berlin')


class AvatarImagePathTestCase(AbstractAppTestCase):

    def setUp(self):
        super().setUp()

        user_id = UUID('2e17cb15-d763-4f93-882a-371296a3c63f')

        self.user = create_user(1)
        self.user.id = user_id

    def test_path(self):
        expected = Path(
            '/var/data/avatars/2e17cb15-d763-4f93-882a-371296a3c63f_1406637810.jpeg')

        with freeze_time('2014-07-29 14:43:30'):
            created_at = TIMEZONE.localize(datetime.now())

        self.user.set_avatar_image(created_at, ImageType.jpeg)

        with self.app.app_context():
            self.app.config['PATH_USER_AVATAR_IMAGES'] = Path('/var/data/avatars')
            self.assertEqual(self.user.avatar_image_path, expected)
