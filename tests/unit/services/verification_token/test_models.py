"""
:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime
from uuid import UUID

from freezegun import freeze_time
import pytest

from byceps.services.verification_token.dbmodels import Token
from byceps.services.verification_token import (
    service as verification_token_service,
)
from byceps.services.verification_token.transfer.models import Purpose


@pytest.mark.parametrize(
    'purpose, now, expected',
    [
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
    ],
)
def test_is_expired(purpose, now, expected):
    token = create_verification_token(purpose)

    with freeze_time(now):
        assert verification_token_service.is_expired(token) == expected


def create_verification_token(purpose):
    user_id = UUID('b57acf68-c258-4b0a-9f00-bb989b36de8a')

    token = Token(user_id, purpose)
    token.created_at = datetime(2014, 11, 26, 17, 44, 53)
    return token
