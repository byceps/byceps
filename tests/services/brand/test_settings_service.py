"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import pytest

from byceps.services.brand import service as brand_service, settings_service
from byceps.services.brand.transfer.models import BrandSetting

from tests.helpers import create_brand


BRAND_ID = 'acmecon'


@pytest.fixture(scope='module')
def brand(party_app_with_db):
    brand = create_brand(BRAND_ID)
    yield brand
    brand_service.delete_brand(brand.id)


def test_create(brand):
    brand_id = BRAND_ID
    name = 'name1'
    value = 'value1'

    assert settings_service.find_setting(brand_id, name) is None

    setting = settings_service.create_setting(brand_id, name, value)

    assert setting is not None
    assert setting.brand_id == brand_id
    assert setting.name == name
    assert setting.value == value


def test_create_or_update(brand):
    brand_id = BRAND_ID
    name = 'name2'
    value1 = 'value2a'
    value2 = 'value2b'

    assert settings_service.find_setting(brand_id, name) is None

    created_setting = settings_service.create_or_update_setting(
        brand_id, name, value1
    )

    assert created_setting is not None
    assert created_setting.brand_id == brand_id
    assert created_setting.name == name
    assert created_setting.value == value1

    updated_setting = settings_service.create_or_update_setting(
        brand_id, name, value2
    )

    assert updated_setting is not None
    assert updated_setting.brand_id == brand_id
    assert updated_setting.name == name
    assert updated_setting.value == value2


def test_remove(brand):
    brand_id = BRAND_ID
    name = 'name3'
    value = 'value3'

    setting = settings_service.create_setting(brand_id, name, value)
    assert settings_service.find_setting(brand_id, name) is not None

    settings_service.remove_setting(brand_id, name)

    assert settings_service.find_setting(brand_id, name) is None


def test_find(brand):
    brand_id = BRAND_ID
    name = 'name4'
    value = 'value4'

    setting_before_create = settings_service.find_setting(brand_id, name)
    assert setting_before_create is None

    settings_service.create_setting(brand_id, name, value)

    setting_after_create = settings_service.find_setting(brand_id, name)
    assert setting_after_create is not None
    assert setting_after_create.brand_id == brand_id
    assert setting_after_create.name == name
    assert setting_after_create.value == value


def test_find_value(brand):
    brand_id = BRAND_ID
    name = 'name5'
    value = 'value5'

    value_before_create = settings_service.find_setting_value(brand_id, name)
    assert value_before_create is None

    settings_service.create_setting(brand_id, name, value)

    value_after_create = settings_service.find_setting_value(brand_id, name)
    assert value_after_create == value


def test_get_settings(brand):
    brand_id = BRAND_ID

    all_settings_before_create = settings_service.get_settings(brand_id)
    assert all_settings_before_create == set()

    for name, value in {
        ('name6a', 'value6a'),
        ('name6b', 'value6b'),
        ('name6c', 'value6c'),
    }:
        settings_service.create_setting(brand_id, name, value)

    all_settings_after_create = settings_service.get_settings(brand_id)
    assert all_settings_after_create == {
        BrandSetting(brand_id, 'name6a', 'value6a'),
        BrandSetting(brand_id, 'name6b', 'value6b'),
        BrandSetting(brand_id, 'name6c', 'value6c'),
    }


def teardown_function(func):
    if func is test_create:
        settings_service.remove_setting(BRAND_ID, 'name1')
    elif func is test_create_or_update:
        settings_service.remove_setting(BRAND_ID, 'name2')
    elif func is test_find:
        settings_service.remove_setting(BRAND_ID, 'name4')
    elif func is test_find_value:
        settings_service.remove_setting(BRAND_ID, 'name5')
    elif func is test_get_settings:
        for name in 'name6a', 'name6b', 'name6c':
            settings_service.remove_setting(BRAND_ID, name)
