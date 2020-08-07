"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import pytest

from byceps.services.user import service as user_service


@pytest.fixture(scope='module')
def named_user(make_user):
    return make_user('HimWhoCanBeNamed')


@pytest.fixture(scope='module')
def unnamed_user(make_user):
    return make_user(None)


def test_find_screen_name_for_unknown_user_id(site_app):
    unknown_user_id = '00000000-0000-0000-0000-000000000000'
    actual = user_service.find_screen_name(unknown_user_id)
    assert actual is None


def test_find_screen_name_for_user_with_screen_name(site_app, named_user):
    actual = user_service.find_screen_name(named_user.id)
    assert actual == 'HimWhoCanBeNamed'


def test_find_screen_name_for_user_without_screen_name(site_app, unnamed_user):
    actual = user_service.find_screen_name(unnamed_user.id)
    assert actual is None
