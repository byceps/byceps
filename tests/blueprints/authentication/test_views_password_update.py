"""
:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.services.authentication.password.models import Credential
from byceps.services.authentication.password import service as password_service
from byceps.services.authentication.session.models import SessionToken

from tests.base import AbstractAppTestCase


class PasswordUpdateTestCase(AbstractAppTestCase):

    def setUp(self):
        super().setUp()

        self.create_brand_and_party()

    def test_when_logged_in_endpoint_is_available(self):
        old_password = 'LekkerBratworsten'
        new_password = 'EvenMoreSecure!!1'

        user = self.create_user()
        password_service.create_password_hash(user.id, old_password)

        credential_before = self.find_credential(user.id)
        assert credential_before is not None

        session_token_before = self.find_session_token(user.id)
        assert session_token_before is not None

        form_data = {
            'old_password': old_password,
            'new_password': new_password,
            'new_password_confirmation': new_password,
        }

        response = self.send_request(form_data, user=user)

        assert response.status_code == 302
        assert response.headers.get('Location') == 'http://example.com/authentication/login'

        credential_after = self.find_credential(user.id)
        session_token_after = self.find_session_token(user.id)

        assert credential_after is not None
        assert credential_before.password_hash != credential_after.password_hash
        assert credential_before.updated_at != credential_after.updated_at

        assert session_token_after is not None
        assert session_token_before.token != session_token_after.token
        assert session_token_before.created_at != session_token_after.created_at

    def test_when_not_logged_in_endpoint_is_unavailable(self):
        form_data = {}

        response = self.send_request(form_data)

        assert response.status_code == 404

    # helpers

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
