# -*- coding: utf-8 -*-

from datetime import datetime
from unittest import TestCase

from nose2.tools import params

from byceps.blueprints.user.models import User, VerificationToken, \
    VerificationTokenPurpose

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
        return self.client.get(url)


def create_confirmation_token(user):
    purpose = VerificationTokenPurpose.email_address_confirmation
    return VerificationToken(user, purpose)
