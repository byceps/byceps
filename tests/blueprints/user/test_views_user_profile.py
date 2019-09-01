"""
:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from tests.base import AbstractAppTestCase
from tests.helpers import create_brand, create_email_config, create_party, \
    create_site, create_user, http_client


class UserProfileTest(AbstractAppTestCase):

    def setUp(self):
        super().setUp()

        brand = create_brand()
        party = create_party(brand.id)
        create_email_config()
        create_site(party.id)

        self.user = create_user()

    def test_view_profile(self):
        url = '/users/{}'.format(self.user.id)

        with http_client(self.app) as client:
            response = client.get(url)

        assert response.status_code == 200
        assert response.mimetype == 'text/html'
