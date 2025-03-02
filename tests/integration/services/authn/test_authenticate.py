"""
:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from secret_type import secret

from byceps.services.authn import authn_service
from byceps.services.authn.errors import AuthenticationFailedError
from byceps.util.result import Err, Ok


CORRECT_PASSWORD = secret('opensesame')
IRRELEVANT_PASSWORD = secret('irrelevant-password')
WRONG_PASSWORD = secret('123456')


def test_unknown_username_is_rejected(make_user):
    actual = authn_service.authenticate('unknown-username', IRRELEVANT_PASSWORD)

    assert actual == Err(AuthenticationFailedError.UsernameUnknown)


def test_uninitialized_user_is_rejected(make_user):
    user = create_user(make_user, initialized=False)

    actual = authn_service.authenticate(user.screen_name, CORRECT_PASSWORD)

    assert actual == Err(AuthenticationFailedError.AccountNotInitialized)


def test_suspended_user_is_rejected(make_user):
    user = create_user(make_user, suspended=True)

    actual = authn_service.authenticate(user.screen_name, CORRECT_PASSWORD)

    assert actual == Err(AuthenticationFailedError.AccountSuspended)


def test_deleted_user_is_rejected(make_user):
    user = create_user(make_user, deleted=True)

    actual = authn_service.authenticate(user.screen_name, CORRECT_PASSWORD)

    assert actual == Err(AuthenticationFailedError.AccountDeleted)


def test_with_wrong_password_is_rejected(make_user):
    user = create_user(make_user)

    actual = authn_service.authenticate(user.screen_name, WRONG_PASSWORD)

    assert actual == Err(AuthenticationFailedError.WrongPassword)


def test_active_user_with_screen_name_and_correct_password_is_accepted(
    make_user,
):
    user = create_user(make_user)

    actual = authn_service.authenticate(user.screen_name, CORRECT_PASSWORD)

    assert actual == Ok(user)


def test_active_user_with_email_address_and_correct_password_is_accepted(
    make_user,
):
    user = create_user(make_user, email_address='ehrenmann@mail.test')

    actual = authn_service.authenticate('ehrenmann@mail.test', CORRECT_PASSWORD)

    assert actual == Ok(user)


def create_user(make_user, **kwargs):
    return make_user(password=CORRECT_PASSWORD, **kwargs)
