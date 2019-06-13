"""
:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from tests.base import AbstractAppTestCase
from tests.helpers import create_user


class UserProfileTest(AbstractAppTestCase):

    def setUp(self):
        super().setUp()

        self.create_brand_and_party()

        self.user = create_user()

    def test_view_profile(self):
        url = '/users/{}'.format(self.user.id)

        with self.client() as client:
            response = client.get(url)

        assert response.status_code == 200
        assert response.mimetype == 'text/html'
