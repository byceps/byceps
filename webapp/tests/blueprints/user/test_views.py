# -*- coding: utf-8 -*-

"""
:Copyright: 2006-2015 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime

from byceps.blueprints.verification_token.models import Purpose, Token
from byceps.blueprints.user.models import User

from tests import AbstractAppTestCase


NOW = datetime.now()


class EmailAddressConfirmationTestCase(AbstractAppTestCase):

    def setUp(self):
        super(EmailAddressConfirmationTestCase, self).setUp()

        self.user = User.create('John', 'john@example.com', 'SuperSecret')
        self.db.session.add(self.user)
        self.db.session.commit()

    def test_confirm_email_address_with_valid_token(self):
        verification_token = create_confirmation_token(self.user)
        self.db.session.add(verification_token)
        self.db.session.commit()

        self.assertFalse(self.user.enabled)

        response = self._confirm(verification_token)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.user.enabled)

    def test_confirm_email_address_with_unknown_token(self):
        verification_token = create_confirmation_token(self.user)
        verification_token.token = '879fa007-5fbc-412e-8ec1-b7f140807631'

        self.assertFalse(self.user.enabled)

        response = self._confirm(verification_token)

        self.assertEqual(response.status_code, 404)
        self.assertFalse(self.user.enabled)

    def _confirm(self, verification_token):
        url = '/users/email_address_confirmations/{}' \
            .format(verification_token.token)
        with self.client() as client:
            return client.get(url)


def create_confirmation_token(user):
    purpose = Purpose.email_address_confirmation
    return Token(user, purpose)
