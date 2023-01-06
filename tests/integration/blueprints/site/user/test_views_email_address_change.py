"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.services.user import user_service
from byceps.services.verification_token import verification_token_service

from tests.helpers import http_client


def test_valid_token(site_app, site, make_user):
    user = make_user(
        email_address='change-success-before@mail.test',
        email_address_verified=True,
    )

    user_before = user_service.get_db_user(user.id)
    assert user_before.email_address == 'change-success-before@mail.test'
    assert user_before.email_address_verified

    token = create_verification_token(user.id, 'change-success-after@mail.test')

    # -------------------------------- #

    response = change(site_app, token)

    # -------------------------------- #

    assert response.status_code == 302

    user_after = user_service.get_db_user(user.id)
    assert user_after.email_address == 'change-success-after@mail.test'
    assert user_after.email_address_verified


def test_unknown_token(site_app, site, make_user):
    user = make_user(
        email_address='change-fail@mail.test',
        email_address_verified=True,
    )

    user_before = user_service.get_db_user(user.id)
    assert user_before.email_address == 'change-fail@mail.test'
    assert user_before.email_address_verified

    unknown_token = 'wZdSLzkT-zRf2x2T6AR7yGa3Nc_X3Nn3F3XGPvPtOhw'

    # -------------------------------- #

    response = change(site_app, unknown_token)

    # -------------------------------- #

    assert response.status_code == 404

    user_after = user_service.get_db_user(user.id)
    assert user_after.email_address == 'change-fail@mail.test'
    assert user_after.email_address_verified


# helpers


def change(app, token):
    url = f'/users/email_address/change/{token}'
    with http_client(app) as client:
        return client.get(url)


def create_verification_token(user_id, new_email_address):
    token = verification_token_service.create_for_email_address_change(
        user_id, new_email_address
    )
    return token.token
