"""
:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.services.party import party_setting_service
from byceps.services.party.transfer.models import PartySetting


PARTY_ID = 'favorite-party'


@pytest.fixture(scope='module')
def party(make_party, brand):
    return make_party(brand.id, PARTY_ID, 'My favorite party!')


def test_create(party):
    party_id = PARTY_ID
    name = 'name1'
    value = 'value1'

    assert party_setting_service.find_setting(party_id, name) is None

    setting = party_setting_service.create_setting(party_id, name, value)

    assert setting is not None
    assert setting.party_id == party_id
    assert setting.name == name
    assert setting.value == value


def test_create_or_update(party):
    party_id = PARTY_ID
    name = 'name2'
    value1 = 'value2a'
    value2 = 'value2b'

    assert party_setting_service.find_setting(party_id, name) is None

    created_setting = party_setting_service.create_or_update_setting(
        party_id, name, value1
    )

    assert created_setting is not None
    assert created_setting.party_id == party_id
    assert created_setting.name == name
    assert created_setting.value == value1

    updated_setting = party_setting_service.create_or_update_setting(
        party_id, name, value2
    )

    assert updated_setting is not None
    assert updated_setting.party_id == party_id
    assert updated_setting.name == name
    assert updated_setting.value == value2


def test_remove(party):
    party_id = PARTY_ID
    name = 'name3'
    value = 'value3'

    party_setting_service.create_setting(party_id, name, value)
    assert party_setting_service.find_setting(party_id, name) is not None

    party_setting_service.remove_setting(party_id, name)

    assert party_setting_service.find_setting(party_id, name) is None


def test_find(party):
    party_id = PARTY_ID
    name = 'name4'
    value = 'value4'

    setting_before_create = party_setting_service.find_setting(party_id, name)
    assert setting_before_create is None

    party_setting_service.create_setting(party_id, name, value)

    setting_after_create = party_setting_service.find_setting(party_id, name)
    assert setting_after_create is not None
    assert setting_after_create.party_id == party_id
    assert setting_after_create.name == name
    assert setting_after_create.value == value


def test_find_value(party):
    party_id = PARTY_ID
    name = 'name5'
    value = 'value5'

    value_before_create = party_setting_service.find_setting_value(
        party_id, name
    )
    assert value_before_create is None

    party_setting_service.create_setting(party_id, name, value)

    value_after_create = party_setting_service.find_setting_value(
        party_id, name
    )
    assert value_after_create == value


def test_get_settings(party):
    party_id = PARTY_ID

    all_settings_before_create = party_setting_service.get_settings(party_id)
    assert all_settings_before_create == set()

    for name, value in {
        ('name6a', 'value6a'),
        ('name6b', 'value6b'),
        ('name6c', 'value6c'),
    }:
        party_setting_service.create_setting(party_id, name, value)

    all_settings_after_create = party_setting_service.get_settings(party_id)
    assert all_settings_after_create == {
        PartySetting(party_id, 'name6a', 'value6a'),
        PartySetting(party_id, 'name6b', 'value6b'),
        PartySetting(party_id, 'name6c', 'value6c'),
    }


def teardown_function(func):
    if func is test_create:
        party_setting_service.remove_setting(PARTY_ID, 'name1')
    elif func is test_create_or_update:
        party_setting_service.remove_setting(PARTY_ID, 'name2')
    elif func is test_find:
        party_setting_service.remove_setting(PARTY_ID, 'name4')
    elif func is test_find_value:
        party_setting_service.remove_setting(PARTY_ID, 'name5')
    elif func is test_get_settings:
        for name in 'name6a', 'name6b', 'name6c':
            party_setting_service.remove_setting(PARTY_ID, name)
