"""
:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.services.brand import brand_setting_service
from byceps.services.brand.models import BrandSetting


BRAND_ID = 'value-brand'


@pytest.fixture(scope='module')
def brand(make_brand):
    return make_brand(BRAND_ID, 'ValueBrand')


def test_create(brand):
    brand_id = BRAND_ID
    name = 'name1'
    value = 'value1'

    assert brand_setting_service.find_setting(brand_id, name) is None

    setting = brand_setting_service.create_setting(brand_id, name, value)

    assert setting is not None
    assert setting.brand_id == brand_id
    assert setting.name == name
    assert setting.value == value


def test_create_or_update(brand):
    brand_id = BRAND_ID
    name = 'name2'
    value1 = 'value2a'
    value2 = 'value2b'

    assert brand_setting_service.find_setting(brand_id, name) is None

    created_setting = brand_setting_service.create_or_update_setting(
        brand_id, name, value1
    )

    assert created_setting is not None
    assert created_setting.brand_id == brand_id
    assert created_setting.name == name
    assert created_setting.value == value1

    updated_setting = brand_setting_service.create_or_update_setting(
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

    brand_setting_service.create_setting(brand_id, name, value)
    assert brand_setting_service.find_setting(brand_id, name) is not None

    brand_setting_service.remove_setting(brand_id, name)

    assert brand_setting_service.find_setting(brand_id, name) is None


def test_find(brand):
    brand_id = BRAND_ID
    name = 'name4'
    value = 'value4'

    setting_before_create = brand_setting_service.find_setting(brand_id, name)
    assert setting_before_create is None

    brand_setting_service.create_setting(brand_id, name, value)

    setting_after_create = brand_setting_service.find_setting(brand_id, name)
    assert setting_after_create is not None
    assert setting_after_create.brand_id == brand_id
    assert setting_after_create.name == name
    assert setting_after_create.value == value


def test_find_value(brand):
    brand_id = BRAND_ID
    name = 'name5'
    value = 'value5'

    value_before_create = brand_setting_service.find_setting_value(
        brand_id, name
    )
    assert value_before_create is None

    brand_setting_service.create_setting(brand_id, name, value)

    value_after_create = brand_setting_service.find_setting_value(
        brand_id, name
    )
    assert value_after_create == value


def test_get_settings(brand):
    brand_id = BRAND_ID

    all_settings_before_create = brand_setting_service.get_settings(brand_id)
    assert all_settings_before_create == set()

    for name, value in {
        ('name6a', 'value6a'),
        ('name6b', 'value6b'),
        ('name6c', 'value6c'),
    }:
        brand_setting_service.create_setting(brand_id, name, value)

    all_settings_after_create = brand_setting_service.get_settings(brand_id)
    assert all_settings_after_create == {
        BrandSetting(brand_id=brand_id, name='name6a', value='value6a'),
        BrandSetting(brand_id=brand_id, name='name6b', value='value6b'),
        BrandSetting(brand_id=brand_id, name='name6c', value='value6c'),
    }


def teardown_function(func):
    if func is test_create:
        brand_setting_service.remove_setting(BRAND_ID, 'name1')
    elif func is test_create_or_update:
        brand_setting_service.remove_setting(BRAND_ID, 'name2')
    elif func is test_find:
        brand_setting_service.remove_setting(BRAND_ID, 'name4')
    elif func is test_find_value:
        brand_setting_service.remove_setting(BRAND_ID, 'name5')
    elif func is test_get_settings:
        for name in 'name6a', 'name6b', 'name6c':
            brand_setting_service.remove_setting(BRAND_ID, name)
