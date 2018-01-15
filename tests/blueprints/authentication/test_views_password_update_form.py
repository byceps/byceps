"""
:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from tests.base import AbstractAppTestCase


class PasswordUpdateFormTestCase(AbstractAppTestCase):

    def setUp(self):
        super().setUp()

        self.create_brand_and_party()

    def test_when_logged_in_form_is_available(self):
        user = self.create_user()
        self.create_session_token(user.id)

        response = self.send_request(user=user)

        assert response.status_code == 200

    def test_when_not_logged_in_form_is_unavailable(self):
        response = self.send_request()

        assert response.status_code == 404

    # helpers

    def send_request(self, *, user=None):
        url = '/authentication/password/update'
        with self.client(user=user) as client:
            return client.get(url)
