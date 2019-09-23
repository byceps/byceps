"""
:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from uuid import UUID

import pytest
from pytest import raises

from byceps.services.user import service as user_service

from tests.helpers import create_user

from ...conftest import database_recreated


@pytest.fixture(scope='module')
def app(admin_app, db):
    with admin_app.app_context():
        with database_recreated(db):
            yield


def test_find_user_by_screen_name_found(app):
    screen_name = 'ghost'

    user = create_user(screen_name)

    actual = user_service.find_user_by_screen_name(screen_name)

    assert actual.id == user.id


def test_find_user_by_screen_name_not_found(app):
    actual = user_service.find_user_by_screen_name('unknown_dude')

    assert actual is None


def test_get_anonymous_user(app):
    user = user_service.get_anonymous_user()

    assert user.id == UUID('00000000-0000-0000-0000-000000000000')

    assert not user.deleted

    assert user.avatar is None
    assert user.avatar_url is None

    assert not user.is_orga


def test_get_email_address_found(app):
    email_address = 'lanparty@lar.ge'

    user = create_user('xpandr', email_address=email_address)

    actual = user_service.get_email_address(user.id)

    assert actual == email_address


def test_get_email_address_not_found(app):
    unknown_user_id = UUID('00000000-0000-0000-0000-000000000001')

    with raises(ValueError):
        user_service.get_email_address(unknown_user_id)
