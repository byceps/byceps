"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import pytest

from byceps.services.user import service as user_service


@pytest.fixture(scope='module')
def user(make_user):
    yield from make_user(
        'CarmenSandiego', email_address='carmen.sandiego@world.example'
    )


def test_find_user_by_email_address_non_lowercase(party_app, user):
    actual = user_service.find_user_by_email_address(
        'Carmen.Sandiego@World.example'
    )
    assert actual is not None
    assert actual.email_address == 'carmen.sandiego@world.example'


def test_find_user_by_email_address_unknown(party_app, user):
    actual = user_service.find_user_by_email_address('no.idea@example.com')
    assert actual is None


def test_find_user_by_screen_name_case_sensitive_match(party_app, user):
    actual = user_service.find_user_by_screen_name('CarmenSandiego')
    assert actual is not None
    assert actual.screen_name == 'CarmenSandiego'


def test_find_user_by_screen_name_case_sensitive_miss(party_app, user):
    actual = user_service.find_user_by_screen_name('cARMENsANDIEGO')
    assert actual is None


def test_find_user_by_screen_name_case_insensitive_match(party_app, user):
    actual = user_service.find_user_by_screen_name(
        'cARMENsANDIEGO', case_insensitive=True
    )
    assert actual is not None
    assert actual.screen_name == 'CarmenSandiego'


def test_find_user_by_screen_name_case_insensitive_miss(party_app, user):
    actual = user_service.find_user_by_screen_name(
        'cARMENsANDIEGOx', case_insensitive=True
    )
    assert actual is None


def test_find_user_by_screen_name_unknown(party_app, user):
    actual = user_service.find_user_by_screen_name('Dunno')
    assert actual is None
