"""
:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.services.authentication.password.models import Credential
from byceps.services.authentication.password import service as password_service
from byceps.services.authentication.session import service as session_service

from tests.base import AbstractAppTestCase
from tests.helpers import create_brand, create_email_config, create_party, \
    create_site, create_user, http_client, login_user


class PasswordUpdateTestCase(AbstractAppTestCase):

    def setUp(self):
        super().setUp()

        brand = create_brand()
        party = create_party(brand.id)
        create_email_config()
        create_site(party.id)

    def test_when_logged_in_endpoint_is_available(self):
        old_password = 'LekkerBratworsten'
        new_password = 'EvenMoreSecure!!1'

        user = create_user()
        password_service.create_password_hash(user.id, old_password)
        login_user(user.id)

        credential_before = self.find_credential(user.id)
        assert credential_before is not None

        session_token_before = self.find_session_token(user.id)
        assert session_token_before is not None

        form_data = {
            'old_password': old_password,
            'new_password': new_password,
            'new_password_confirmation': new_password,
        }

        response = self.send_request(form_data, user_id=user.id)

        assert response.status_code == 302
        assert response.headers.get('Location') == 'http://example.com/authentication/login'

        credential_after = self.find_credential(user.id)
        session_token_after = self.find_session_token(user.id)

        assert credential_after is not None
        assert credential_before.password_hash != credential_after.password_hash
        assert credential_before.updated_at != credential_after.updated_at

        # Session token should have been removed after password change.
        assert session_token_after is None

    def test_when_not_logged_in_endpoint_is_unavailable(self):
        form_data = {}

        response = self.send_request(form_data)

        assert response.status_code == 404

    # helpers

    def find_credential(self, user_id):
        return Credential.query.get(user_id)

    def find_session_token(self, user_id):
        return session_service.find_session_token_for_user(user_id)

    def send_request(self, form_data, *, user_id=None):
        url = '/authentication/password'
        with http_client(self.app, user_id=user_id) as client:
            return client.post(url, data=form_data)
