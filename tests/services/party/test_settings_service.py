"""
:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import pytest

from byceps.services.party.models.setting import Setting as DbSetting
from byceps.services.party import settings_service
from byceps.services.party.transfer.models import PartySetting

from tests.helpers import create_brand, create_party

from ...conftest import database_recreated


@pytest.fixture(scope='module')
def app(party_app, db):
    with party_app.app_context():
        with database_recreated(db):
            _app = party_app

            brand = create_brand()
            party = create_party(brand.id)

            _app.party_id = party.id

            yield _app


def test_create(app):
    party_id = app.party_id
    name = 'name1'
    value = 'value1'

    assert settings_service.find_setting(party_id, name) is None

    setting = settings_service.create_setting(party_id, name, value)

    assert setting is not None
    assert setting.party_id == party_id
    assert setting.name == name
    assert setting.value == value


def test_create_or_update(app):
    party_id = app.party_id
    name = 'name2'
    value1 = 'value2a'
    value2 = 'value2b'

    assert settings_service.find_setting(party_id, name) is None

    created_setting = settings_service \
        .create_or_update_setting(party_id, name, value1)

    assert created_setting is not None
    assert created_setting.party_id == party_id
    assert created_setting.name == name
    assert created_setting.value == value1

    updated_setting = settings_service \
        .create_or_update_setting(party_id, name, value2)

    assert updated_setting is not None
    assert updated_setting.party_id == party_id
    assert updated_setting.name == name
    assert updated_setting.value == value2


def test_find(app):
    party_id = app.party_id
    name = 'name3'
    value = 'value3'

    setting_before_create = settings_service.find_setting(party_id, name)
    assert setting_before_create is None

    settings_service.create_setting(party_id, name, value)

    setting_after_create = settings_service.find_setting(party_id, name)
    assert setting_after_create is not None
    assert setting_after_create.party_id == party_id
    assert setting_after_create.name == name
    assert setting_after_create.value == value


def test_find_value(app):
    party_id = app.party_id
    name = 'name4'
    value = 'value4'

    value_before_create = settings_service.find_setting_value(party_id, name)
    assert value_before_create is None

    settings_service.create_setting(party_id, name, value)

    value_after_create = settings_service.find_setting_value(party_id, name)
    assert value_after_create == value


def test_get_settings(app):
    party_id = app.party_id

    # Clean up.
    DbSetting.query.delete()

    all_settings_before_create = settings_service.get_settings(party_id)
    assert all_settings_before_create == set()

    for name, value in {
        ('name5a', 'value5a'),
        ('name5b', 'value5b'),
        ('name5c', 'value5c'),
    }:
        settings_service.create_setting(party_id, name, value)

    all_settings_after_create = settings_service.get_settings(party_id)
    assert all_settings_after_create == {
        PartySetting(party_id, 'name5a', 'value5a'),
        PartySetting(party_id, 'name5b', 'value5b'),
        PartySetting(party_id, 'name5c', 'value5c'),
    }
