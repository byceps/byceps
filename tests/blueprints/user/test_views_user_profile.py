"""
:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from tests.base import AbstractAppTestCase
from tests.helpers import (
    create_email_config,
    create_site,
    create_user,
    http_client,
)


class UserProfileTest(AbstractAppTestCase):

    def setUp(self):
        super().setUp()

        create_email_config()
        create_site()

        self.user = create_user()

    def test_view_profile(self):
        url = f'/users/{self.user.id}'

        with http_client(self.app) as client:
            response = client.get(url)

        assert response.status_code == 200
        assert response.mimetype == 'text/html'
