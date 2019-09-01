"""
:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from tests.base import AbstractAppTestCase
from tests.helpers import create_brand, create_email_config, create_party, \
    create_site, create_user, http_client


class HomePageTest(AbstractAppTestCase):

    def setUp(self):
        super().setUp()

        brand = create_brand()
        party = create_party(brand.id)
        create_email_config()
        create_site(party.id)

    def test_homepage(self):
        with http_client(self.app) as client:
            response = client.get('/')

        # By default, nothing is mounted on `/`, but at least check that
        # the application boots up and doesn't return a server error.
        assert response.status_code == 404
