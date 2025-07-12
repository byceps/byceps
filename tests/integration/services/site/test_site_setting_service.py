"""
:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.services.site import site_service, site_setting_service
from byceps.services.site.models import SiteSetting

from tests.helpers import create_site


SITE_ID = 'favorite-site'


@pytest.fixture(scope='module')
def site(admin_app, brand):
    site = create_site(
        SITE_ID,
        brand.id,
        title='My favorite site!',
        server_name='www.favorite-site.test',
    )
    yield site
    site_service.delete_site(site.id)


def test_create(site):
    site_id = SITE_ID
    name = 'name1'
    value = 'value1'

    assert site_setting_service.find_setting(site_id, name) is None

    setting = site_setting_service.create_setting(site_id, name, value)

    assert setting is not None
    assert setting.site_id == site_id
    assert setting.name == name
    assert setting.value == value


def test_create_or_update(site):
    site_id = SITE_ID
    name = 'name2'
    value1 = 'value2a'
    value2 = 'value2b'

    assert site_setting_service.find_setting(site_id, name) is None

    created_setting = site_setting_service.create_or_update_setting(
        site_id, name, value1
    )

    assert created_setting is not None
    assert created_setting.site_id == site_id
    assert created_setting.name == name
    assert created_setting.value == value1

    updated_setting = site_setting_service.create_or_update_setting(
        site_id, name, value2
    )

    assert updated_setting is not None
    assert updated_setting.site_id == site_id
    assert updated_setting.name == name
    assert updated_setting.value == value2


def test_remove(site):
    site_id = SITE_ID
    name = 'name3'
    value = 'value3'

    site_setting_service.create_setting(site_id, name, value)
    assert site_setting_service.find_setting(site_id, name) is not None

    site_setting_service.remove_setting(site_id, name)

    assert site_setting_service.find_setting(site_id, name) is None


def test_find(site):
    site_id = SITE_ID
    name = 'name4'
    value = 'value4'

    setting_before_create = site_setting_service.find_setting(site_id, name)
    assert setting_before_create is None

    site_setting_service.create_setting(site_id, name, value)

    setting_after_create = site_setting_service.find_setting(site_id, name)
    assert setting_after_create is not None
    assert setting_after_create.site_id == site_id
    assert setting_after_create.name == name
    assert setting_after_create.value == value


def test_find_value(site):
    site_id = SITE_ID
    name = 'name5'
    value = 'value5'

    value_before_create = site_setting_service.find_setting_value(site_id, name)
    assert value_before_create is None

    site_setting_service.create_setting(site_id, name, value)

    value_after_create = site_setting_service.find_setting_value(site_id, name)
    assert value_after_create == value


def test_get_settings(site):
    site_id = SITE_ID

    all_settings_before_create = site_setting_service.get_settings(site_id)
    assert all_settings_before_create == set()

    for name, value in {
        ('name6a', 'value6a'),
        ('name6b', 'value6b'),
        ('name6c', 'value6c'),
    }:
        site_setting_service.create_setting(site_id, name, value)

    all_settings_after_create = site_setting_service.get_settings(site_id)
    assert all_settings_after_create == {
        SiteSetting(site_id=site_id, name='name6a', value='value6a'),
        SiteSetting(site_id=site_id, name='name6b', value='value6b'),
        SiteSetting(site_id=site_id, name='name6c', value='value6c'),
    }


def teardown_function(func):
    if func is test_create:
        site_setting_service.remove_setting(SITE_ID, 'name1')
    elif func is test_create_or_update:
        site_setting_service.remove_setting(SITE_ID, 'name2')
    elif func is test_find:
        site_setting_service.remove_setting(SITE_ID, 'name4')
    elif func is test_find_value:
        site_setting_service.remove_setting(SITE_ID, 'name5')
    elif func is test_get_settings:
        for name in 'name6a', 'name6b', 'name6c':
            site_setting_service.remove_setting(SITE_ID, name)
