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


class HomePageTest(AbstractAppTestCase):

    def setUp(self):
        super().setUp()

        create_email_config()
        create_site()

    def test_homepage(self):
        with http_client(self.app) as client:
            response = client.get('/')

        # By default, nothing is mounted on `/`, but at least check that
        # the application boots up and doesn't return a server error.
        assert response.status_code == 404
