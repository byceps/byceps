# -*- coding: utf-8 -*-

"""
:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime
from unittest import TestCase

from freezegun import freeze_time
from nose2.tools import params

from byceps.blueprints.verification_token.models import Purpose, Token
from byceps.blueprints.user.models import User


class TokenTest(TestCase):

    @params(
        (
            Purpose.email_address_confirmation,
            datetime(2014, 11, 26, 19, 54, 38),
            False,
        ),
        (
            Purpose.email_address_confirmation,
            datetime(2014, 11, 27, 19, 54, 38),
            False,  # Never expires.
        ),
        (
            Purpose.password_reset,
            datetime(2014, 11, 26, 19, 54, 38),
            False,
        ),
        (
            Purpose.password_reset,
            datetime(2014, 11, 27, 17, 44, 52),
            False,  # Almost, but not yet.
        ),
        (
            Purpose.password_reset,
            datetime(2014, 11, 27, 17, 44, 53),
            True,  # Just now.
        ),
        (
            Purpose.password_reset,
            datetime(2014, 11, 27, 19, 54, 38),
            True,
        ),
    )
    def test_is_expired(self, purpose, now, expected):
        user = User()
        token = Token(user, purpose)
        token.created_at = datetime(2014, 11, 26, 17, 44, 53)

        with freeze_time(now):
            self.assertEqual(token.is_expired, expected)
