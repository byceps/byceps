"""
:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime

import pytest

from byceps.services.brand import service as brand_service
from byceps.services.party import service as party_service, settings_service
from byceps.services.party.transfer.models import PartySetting


@pytest.fixture
def app(party_app_with_db):
    _app = party_app_with_db

    brand = brand_service.create_brand('acme', 'ACME')

    now = datetime.utcnow()
    party = party_service.create_party('acmeparty', brand.id, 'ACME Party',
                                       now, now)
    _app.party_id = party.id

    yield _app


def test_create(app):
    party_id = app.party_id
    name = 'name'
    value = 'value'

    assert settings_service.find_setting(party_id, name) is None

    setting = settings_service.create_setting(party_id, name, value)

    assert setting is not None
    assert setting.party_id == party_id
    assert setting.name == name
    assert setting.value == value

def test_create_or_update(app):
    party_id = app.party_id
    name = 'name'
    value1 = 'value1'
    value2 = 'value2'

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
    name = 'name'
    value = 'value'

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
    name = 'name'
    value = 'value'

    value_before_create = settings_service.find_setting_value(party_id, name)
    assert value_before_create is None

    settings_service.create_setting(party_id, name, value)

    value_after_create = settings_service.find_setting_value(party_id, name)
    assert value_after_create == value

def test_get_settings(app):
    party_id = app.party_id

    all_settings_before_create = settings_service.get_settings(party_id)
    assert all_settings_before_create == set()

    for name, value in {
        ('name1', 'value1'),
        ('name2', 'value2'),
        ('name3', 'value3'),
    }:
        settings_service.create_setting(party_id, name, value)

    all_settings_after_create = settings_service.get_settings(party_id)
    assert all_settings_after_create == {
        PartySetting(party_id, 'name1', 'value1'),
        PartySetting(party_id, 'name2', 'value2'),
        PartySetting(party_id, 'name3', 'value3'),
    }
