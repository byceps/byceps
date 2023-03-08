"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from pytest import raises

from byceps.services.authentication import authn_service
from byceps.services.authentication.exceptions import (
    AccountDeleted,
    AccountNotInitialized,
    AccountSuspended,
    UsernameUnknown,
    WrongPassword,
)


CORRECT_PASSWORD = 'opensesame'
WRONG_PASSWORD = '123456'


def test_unknown_username_is_rejected(make_user):
    with raises(UsernameUnknown):
        authn_service.authenticate('unknown-username', 'irrelevant-password')


def test_uninitialized_user_is_rejected(make_user):
    user = create_user(make_user, initialized=False)

    with raises(AccountNotInitialized):
        authn_service.authenticate(user.screen_name, CORRECT_PASSWORD)


def test_suspended_user_is_rejected(make_user):
    user = create_user(make_user, suspended=True)

    with raises(AccountSuspended):
        authn_service.authenticate(user.screen_name, CORRECT_PASSWORD)


def test_deleted_user_is_rejected(make_user):
    user = create_user(make_user, deleted=True)

    with raises(AccountDeleted):
        authn_service.authenticate(user.screen_name, CORRECT_PASSWORD)


def test_with_wrong_password_is_rejected(make_user):
    user = create_user(make_user)

    with raises(WrongPassword):
        authn_service.authenticate(user.screen_name, WRONG_PASSWORD)


def test_active_user_with_screen_name_and_correct_password_is_accepted(
    make_user,
):
    user = create_user(make_user)

    actual = authn_service.authenticate(user.screen_name, CORRECT_PASSWORD)

    assert actual == user


def test_active_user_with_email_address_and_correct_password_is_accepted(
    make_user,
):
    user = create_user(make_user, email_address='ehrenmann@mail.test')

    actual = authn_service.authenticate('ehrenmann@mail.test', CORRECT_PASSWORD)

    assert actual == user


def create_user(make_user, **kwargs):
    return make_user(password=CORRECT_PASSWORD, **kwargs)
