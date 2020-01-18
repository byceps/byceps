"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime

from freezegun import freeze_time
import pytest

from byceps.services.verification_token.models import Purpose

from testfixtures.user import create_user
from testfixtures.verification_token import create_verification_token


@pytest.mark.parametrize('purpose, now, expected', [
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
])
def test_is_expired(purpose, now, expected):
    user = create_user()
    created_at = datetime(2014, 11, 26, 17, 44, 53)

    token = create_verification_token(user.id, purpose, created_at=created_at)

    with freeze_time(now):
        assert token.is_expired == expected
