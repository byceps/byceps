"""
:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from tests.base import AbstractAppTestCase
from tests.helpers import create_brand, create_email_config, create_party, \
    create_site, create_user, http_client

from testfixtures.verification_token import \
    create_verification_token_for_email_address_confirmation \
    as create_confirmation_token


class EmailAddressConfirmationTestCase(AbstractAppTestCase):

    def setUp(self):
        super().setUp()

        brand = create_brand()
        party = create_party(brand.id)
        create_email_config()
        create_site(party.id)

        self.user = create_user(enabled=False)
        assert not self.user.enabled

    def test_confirm_email_address_with_valid_token(self):
        verification_token = create_confirmation_token(self.user.id)
        self.db.session.add(verification_token)
        self.db.session.commit()

        response = self._confirm(verification_token)

        assert response.status_code == 302
        assert self.user.enabled

    def test_confirm_email_address_with_unknown_token(self):
        verification_token = create_confirmation_token(self.user.id)
        verification_token.token = 'wZdSLzkT-zRf2x2T6AR7yGa3Nc_X3Nn3F3XGPvPtOhw'

        response = self._confirm(verification_token)

        assert response.status_code == 404
        assert not self.user.enabled

    def _confirm(self, verification_token):
        url = '/users/email_address/confirmation/{}' \
            .format(verification_token.token)
        with http_client(self.app) as client:
            return client.get(url)
