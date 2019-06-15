"""
:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from tests.base import AbstractAppTestCase
from tests.helpers import create_brand, create_party, create_session_token, \
    create_user


class PasswordUpdateFormTestCase(AbstractAppTestCase):

    def setUp(self):
        super().setUp()

        brand = create_brand()
        create_party(brand_id=brand.id)

    def test_when_logged_in_form_is_available(self):
        user = create_user()
        create_session_token(user.id)

        response = self.send_request(user_id=user.id)

        assert response.status_code == 200

    def test_when_not_logged_in_form_is_unavailable(self):
        response = self.send_request()

        assert response.status_code == 404

    # helpers

    def send_request(self, *, user_id=None):
        url = '/authentication/password/update'
        with self.client(user_id=user_id) as client:
            return client.get(url)
