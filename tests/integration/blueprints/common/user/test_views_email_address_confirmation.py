"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.database import db
from byceps.services.authorization import service as authorization_service
from byceps.services.user import service as user_service
from byceps.services.verification_token.models import Purpose, Token

from tests.helpers import http_client


@pytest.fixture(scope='module')
def user1(make_user):
    return make_user('EAC-User1', initialized=False)


@pytest.fixture(scope='module')
def user2(make_user):
    return make_user('EAC-User2', initialized=False)


@pytest.fixture
def role(admin_app, site, user1, user2):
    role = authorization_service.create_role('board_user', 'Board User')

    yield role

    for user in user1, user2:
        authorization_service.deassign_all_roles_from_user(user.id)

    authorization_service.delete_role(role.id)


def test_confirm_email_address_with_valid_token(site_app, user1, role):
    user = user1

    verification_token = create_confirmation_token(user.id)
    db.session.add(verification_token)
    db.session.commit()

    # -------------------------------- #

    response = confirm(site_app, verification_token)

    # -------------------------------- #

    assert response.status_code == 302
    assert is_user_initialized(user.id)
    assert get_role_ids(user.id) == {'board_user'}


def test_confirm_email_address_with_unknown_token(site_app, site, user2, role):
    user = user2

    verification_token = create_confirmation_token(user.id)
    verification_token.token = 'wZdSLzkT-zRf2x2T6AR7yGa3Nc_X3Nn3F3XGPvPtOhw'

    # -------------------------------- #

    response = confirm(site_app, verification_token)

    # -------------------------------- #

    assert response.status_code == 404
    assert not is_user_initialized(user.id)
    assert get_role_ids(user.id) == set()


# helpers


def confirm(app, verification_token):
    url = f'/users/email_address/confirmation/{verification_token.token}'
    with http_client(app) as client:
        return client.get(url)


def is_user_initialized(user_id) -> bool:
    user = user_service.get_db_user(user_id)
    return bool(user.initialized)


def get_role_ids(user_id):
    return authorization_service.find_role_ids_for_user(user_id)


def create_confirmation_token(user_id):
    purpose = Purpose.email_address_confirmation
    return Token(user_id, purpose)
