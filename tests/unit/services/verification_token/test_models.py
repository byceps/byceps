"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from freezegun import freeze_time
import pytest

from byceps.services.verification_token import verification_token_service
from byceps.services.verification_token.models import PasswordResetToken


@pytest.mark.parametrize(
    ('now', 'expected'),
    [
        (datetime(2014, 11, 26, 19, 54, 38), False),
        (datetime(2014, 11, 27, 17, 44, 52), False),  # Almost, but not yet.
        (datetime(2014, 11, 27, 17, 44, 53), True),  # Just now.
        (datetime(2014, 11, 27, 19, 54, 38), True),
    ],
)
def test_is_expired(user, now, expected):
    reset_token = PasswordResetToken(
        token='fake',  # noqa: S106
        created_at=datetime(2014, 11, 26, 17, 44, 53),
        user=user,
    )

    with freeze_time(now):
        assert verification_token_service.is_expired(reset_token) == expected
