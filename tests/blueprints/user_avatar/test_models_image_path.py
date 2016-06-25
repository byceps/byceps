# -*- coding: utf-8 -*-

"""
:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from pathlib import Path
from uuid import UUID

from byceps.util.image import ImageType

from tests.base import AbstractAppTestCase

from testfixtures.user import create_user
from testfixtures.user_avatar import create_avatar


class AvatarImagePathTestCase(AbstractAppTestCase):

    def setUp(self):
        super().setUp()

        self.user = create_user(1)

    def test_path(self):
        avatar_id = UUID('2e17cb15-d763-4f93-882a-371296a3c63f')

        expected = Path(
            '/var/data/avatars/2e17cb15-d763-4f93-882a-371296a3c63f.jpeg')

        avatar = create_avatar(self.user, id=avatar_id, image_type=ImageType.jpeg)

        with self.app.app_context():
            self.app.config['PATH_USER_AVATAR_IMAGES'] = Path('/var/data/avatars')
            self.assertEqual(avatar.path, expected)
