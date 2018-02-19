"""
:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from tests.base import AbstractAppTestCase


class CurrentUserTestCase(AbstractAppTestCase):

    def setUp(self):
        super().setUp()

        self.create_brand_and_party()

    def test_when_logged_in(self):
        user = self.create_user('McFly')
        self.create_session_token(user.id)

        response = self.send_request(user=user)

        assert response.status_code == 200
        assert response.mimetype == 'text/html'

    def test_when_not_logged_in(self):
        response = self.send_request()

        assert response.status_code == 302
        assert 'Location' in response.headers

    # helpers

    def send_request(self, *, user=None):
        url = '/users/me'
        with self.client(user=user) as client:
            return client.get(url)
