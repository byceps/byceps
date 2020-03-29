"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import pytest

from byceps.services.user import service as user_service

from tests.conftest import database_recreated
from tests.helpers import create_user


@pytest.fixture(scope='module')
def app(party_app, db):
    with party_app.app_context():
        with database_recreated(db):
            yield party_app


@pytest.fixture(scope='module')
def user():
    return create_user(
        'CarmenSandiego', email_address='carmen.sandiego@world.example'
    )


def test_find_user_by_email_address_non_lowercase(app, user):
    actual = user_service.find_user_by_email_address(
        'Carmen.Sandiego@World.example'
    )
    assert actual is not None
    assert actual.email_address == 'carmen.sandiego@world.example'


def test_find_user_by_email_address_unknown(app, user):
    actual = user_service.find_user_by_email_address('no.idea@example.com')
    assert actual is None


def test_find_user_by_screen_name_case_sensitive_match(app, user):
    actual = user_service.find_user_by_screen_name('CarmenSandiego')
    assert actual is not None
    assert actual.screen_name == 'CarmenSandiego'


def test_find_user_by_screen_name_case_sensitive_miss(app, user):
    actual = user_service.find_user_by_screen_name('cARMENsANDIEGO')
    assert actual is None


def test_find_user_by_screen_name_case_insensitive_match(app, user):
    actual = user_service.find_user_by_screen_name(
        'cARMENsANDIEGO', case_insensitive=True
    )
    assert actual is not None
    assert actual.screen_name == 'CarmenSandiego'


def test_find_user_by_screen_name_case_insensitive_miss(app, user):
    actual = user_service.find_user_by_screen_name(
        'cARMENsANDIEGOx', case_insensitive=True
    )
    assert actual is None


def test_find_user_by_screen_name_unknown(app, user):
    actual = user_service.find_user_by_screen_name('Dunno')
    assert actual is None
