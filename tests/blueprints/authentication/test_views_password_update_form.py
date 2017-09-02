"""
:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from tests.base import AbstractAppTestCase

from testfixtures.authentication import create_session_token


class PasswordUpdateFormTestCase(AbstractAppTestCase):

    def test_when_logged_in_form_is_available(self):
        user = self.create_user()
        self.create_session_token(user.id)

        response = self.send_request(user=user)

        self.assertEqual(response.status_code, 200)

    def test_when_not_logged_in_form_is_unavailable(self):
        response = self.send_request()

        self.assertEqual(response.status_code, 404)

    # helpers

    def create_session_token(self, user_id):
        session_token = create_session_token(user_id)

        self.db.session.add(session_token)
        self.db.session.commit()

    def send_request(self, *, user=None):
        url = '/authentication/password/update'
        with self.client(user=user) as client:
            return client.get(url)
