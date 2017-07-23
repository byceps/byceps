"""
:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.services.authentication.password.models import Credential
from byceps.services.authentication.password import service as password_service
from byceps.services.authentication.session.models import SessionToken

from tests.base import AbstractAppTestCase

from testfixtures.user import create_user


class PasswordUpdateTestCase(AbstractAppTestCase):

    def test_when_logged_in_endpoint_is_available(self):
        old_password = 'LekkerBratworsten'
        new_password = 'EvenMoreSecure!!1'

        user = self.create_user(old_password)

        credential_before = self.find_credential(user.id)
        self.assertIsNotNone(credential_before)

        session_token_before = self.find_session_token(user.id)
        self.assertIsNotNone(session_token_before)

        form_data = {
            'old_password': old_password,
            'new_password': new_password,
            'new_password_confirmation': new_password,
        }

        response = self.send_request(form_data, user=user)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers.get('Location'),
            'http://example.com/authentication/login')

        credential_after = self.find_credential(user.id)
        session_token_after = self.find_session_token(user.id)

        self.assertIsNotNone(credential_after)
        self.assertNotEqual(credential_before.password_hash,
                            credential_after.password_hash)
        self.assertNotEqual(credential_before.updated_at,
                            credential_after.updated_at)

        self.assertIsNotNone(session_token_after)
        self.assertNotEqual(session_token_before.token,
                            session_token_after.token)
        self.assertNotEqual(session_token_before.created_at,
                            session_token_after.created_at)

    def test_when_not_logged_in_endpoint_is_unavailable(self):
        form_data = {}

        response = self.send_request(form_data)

        self.assertEqual(response.status_code, 404)

    # helpers

    def create_user(self, password):
        user = create_user()

        self.db.session.add(user)
        self.db.session.commit()

        password_service.create_password_hash(user.id, password)

        return user

    def find_credential(self, user_id):
        return Credential.query.get(user_id)

    def find_session_token(self, user_id):
        return SessionToken.query \
            .filter_by(user_id=user_id) \
            .one()

    def send_request(self, form_data, *, user=None):
        url = '/authentication/password'
        with self.client(user=user) as client:
            return client.post(url, data=form_data)
