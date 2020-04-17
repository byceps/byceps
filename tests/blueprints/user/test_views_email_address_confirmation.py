"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import pytest

from byceps.services.authorization import service as authorization_service
from byceps.services.user import command_service as user_command_service
from byceps.services.verification_token.models import Purpose, Token

from tests.conftest import database_recreated
from tests.helpers import create_site, create_user, http_client


@pytest.fixture(scope='module')
def app(party_app, db, make_email_config):
    with party_app.app_context():
        with database_recreated(db):
            make_email_config()
            create_site()
            yield party_app


@pytest.fixture(scope='module')
def user1(db):
    user = create_user('User1', initialized=False)
    yield user
    user_command_service.delete_account(user.id, user.id, 'clean up')


@pytest.fixture(scope='module')
def user2(db):
    user = create_user('User2', initialized=False)
    yield user
    user_command_service.delete_account(user.id, user.id, 'clean up')


@pytest.fixture(scope='module')
def role(app, user1, user2):
    role = authorization_service.create_role('board_user', 'Board User')

    yield role

    for user in user1, user2:
        authorization_service.deassign_all_roles_from_user(user.id)

    authorization_service.delete_role(role.id)


def test_confirm_email_address_with_valid_token(app, db, user1, role):
    user = user1

    verification_token = create_confirmation_token(user.id)
    db.session.add(verification_token)
    db.session.commit()

    # -------------------------------- #

    response = confirm(app, verification_token)

    # -------------------------------- #

    assert response.status_code == 302
    assert user.initialized
    assert get_role_ids(user.id) == {'board_user'}


def test_confirm_email_address_with_unknown_token(app, user2, role):
    user = user2

    verification_token = create_confirmation_token(user.id)
    verification_token.token = 'wZdSLzkT-zRf2x2T6AR7yGa3Nc_X3Nn3F3XGPvPtOhw'

    # -------------------------------- #

    response = confirm(app, verification_token)

    # -------------------------------- #

    assert response.status_code == 404
    assert not user.initialized
    assert get_role_ids(user.id) == set()


# helpers


def confirm(app, verification_token):
    url = f'/users/email_address/confirmation/{verification_token.token}'
    with http_client(app) as client:
        return client.get(url)


def get_role_ids(user_id):
    return authorization_service.find_role_ids_for_user(user_id)


def create_confirmation_token(user_id):
    purpose = Purpose.email_address_confirmation
    return Token(user_id, purpose)
