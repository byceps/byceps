"""
:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.services.global_setting import global_setting_service
from byceps.services.global_setting.transfer.models import GlobalSetting


def test_create(admin_app):
    name = 'name1'
    value = 'value1'

    assert global_setting_service.find_setting(name) is None

    setting = global_setting_service.create_setting(name, value)

    assert setting is not None
    assert setting.name == name
    assert setting.value == value


def test_create_or_update(admin_app):
    name = 'name2'
    value1 = 'value2a'
    value2 = 'value2b'

    assert global_setting_service.find_setting(name) is None

    created_setting = global_setting_service.create_or_update_setting(
        name, value1
    )

    assert created_setting is not None
    assert created_setting.name == name
    assert created_setting.value == value1

    updated_setting = global_setting_service.create_or_update_setting(
        name, value2
    )

    assert updated_setting is not None
    assert updated_setting.name == name
    assert updated_setting.value == value2


def test_remove(admin_app):
    name = 'name3'
    value = 'value3'

    global_setting_service.create_setting(name, value)
    assert global_setting_service.find_setting(name) is not None

    global_setting_service.remove_setting(name)

    assert global_setting_service.find_setting(name) is None


def test_find(admin_app):
    name = 'name4'
    value = 'value4'

    setting_before_create = global_setting_service.find_setting(name)
    assert setting_before_create is None

    global_setting_service.create_setting(name, value)

    setting_after_create = global_setting_service.find_setting(name)
    assert setting_after_create is not None
    assert setting_after_create.name == name
    assert setting_after_create.value == value


def test_find_value(admin_app):
    name = 'name5'
    value = 'value5'

    value_before_create = global_setting_service.find_setting_value(name)
    assert value_before_create is None

    global_setting_service.create_setting(name, value)

    value_after_create = global_setting_service.find_setting_value(name)
    assert value_after_create == value


def test_get_settings(admin_app):
    all_settings_before_create = global_setting_service.get_settings()
    assert all_settings_before_create == set()

    for name, value in {
        ('name6a', 'value6a'),
        ('name6b', 'value6b'),
        ('name6c', 'value6c'),
    }:
        global_setting_service.create_setting(name, value)

    all_settings_after_create = global_setting_service.get_settings()
    assert all_settings_after_create == {
        GlobalSetting('name6a', 'value6a'),
        GlobalSetting('name6b', 'value6b'),
        GlobalSetting('name6c', 'value6c'),
    }


def teardown_function(func):
    if func is test_create:
        global_setting_service.remove_setting('name1')
    elif func is test_create_or_update:
        global_setting_service.remove_setting('name2')
    elif func is test_find:
        global_setting_service.remove_setting('name4')
    elif func is test_find_value:
        global_setting_service.remove_setting('name5')
    elif func is test_get_settings:
        for name in 'name6a', 'name6b', 'name6c':
            global_setting_service.remove_setting(name)
