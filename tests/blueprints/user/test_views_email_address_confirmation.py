"""
:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime

from tests.base import AbstractAppTestCase

from testfixtures.verification_token import \
    create_verification_token_for_email_address_confirmation \
    as create_confirmation_token


NOW = datetime.now()


class EmailAddressConfirmationTestCase(AbstractAppTestCase):

    def setUp(self):
        super().setUp()

        self.user = self.create_user(enabled=False)

        self.create_brand_and_party()

    def test_confirm_email_address_with_valid_token(self):
        verification_token = create_confirmation_token(self.user.id)
        self.db.session.add(verification_token)
        self.db.session.commit()

        assert not self.user.enabled

        response = self._confirm(verification_token)

        assert response.status_code == 302
        assert self.user.enabled

    def test_confirm_email_address_with_unknown_token(self):
        verification_token = create_confirmation_token(self.user.id)
        verification_token.token = '879fa007-5fbc-412e-8ec1-b7f140807631'

        assert not self.user.enabled

        response = self._confirm(verification_token)

        assert response.status_code == 404
        assert not self.user.enabled

    def _confirm(self, verification_token):
        url = '/users/email_address_confirmations/{}' \
            .format(verification_token.token)
        with self.client() as client:
            return client.get(url)
