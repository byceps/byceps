# -*- coding: utf-8 -*-

from datetime import datetime
from unittest import TestCase

from freezegun import freeze_time
from nose2.tools import params

from byceps.blueprints.user.models import User, VerificationToken, \
    VerificationTokenPurpose


class VerificationTokenTest(TestCase):

    @params(
        (
            VerificationTokenPurpose.email_address_confirmation,
            datetime(2014, 11, 26, 19, 54, 38),
            False,
        ),
        (
            VerificationTokenPurpose.email_address_confirmation,
            datetime(2014, 11, 27, 19, 54, 38),
            False,  # Never expires.
        ),
        (
            VerificationTokenPurpose.password_reset,
            datetime(2014, 11, 26, 19, 54, 38),
            False,
        ),
        (
            VerificationTokenPurpose.password_reset,
            datetime(2014, 11, 27, 17, 44, 52),
            False,  # Almost, but not yet.
        ),
        (
            VerificationTokenPurpose.password_reset,
            datetime(2014, 11, 27, 17, 44, 53),
            True,  # Just now.
        ),
        (
            VerificationTokenPurpose.password_reset,
            datetime(2014, 11, 27, 19, 54, 38),
            True,
        ),
    )
    def test_is_expired(self, purpose, now, expected):
        user = User()
        token = VerificationToken(user, purpose)
        token.created_at = datetime(2014, 11, 26, 17, 44, 53)

        with freeze_time(now):
            self.assertEquals(token.is_expired, expected)
