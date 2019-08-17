"""
:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime

import pytest

from byceps.services.brand import service as brand_service
from byceps.services.party import service as party_service
from byceps.services.site import service as site_service, settings_service
from byceps.services.site.transfer.models import SiteSetting


@pytest.fixture
def app(party_app_with_db):
    _app = party_app_with_db

    brand = brand_service.create_brand('acme', 'ACME')

    now = datetime.utcnow()
    party = party_service.create_party('acmeparty', brand.id, 'ACME Party',
                                       now, now)

    site = site_service.create_site('acme-intranet', party.id,
                                    'ACME Party Intranet', 'www.example.com')
    _app.site_id = site.id

    yield _app


def test_create(app):
    site_id = app.site_id
    name = 'name'
    value = 'value'

    assert settings_service.find_setting(site_id, name) is None

    setting = settings_service.create_setting(site_id, name, value)

    assert setting is not None
    assert setting.site_id == site_id
    assert setting.name == name
    assert setting.value == value

def test_create_or_update(app):
    site_id = app.site_id
    name = 'name'
    value1 = 'value1'
    value2 = 'value2'

    assert settings_service.find_setting(site_id, name) is None

    created_setting = settings_service \
        .create_or_update_setting(site_id, name, value1)

    assert created_setting is not None
    assert created_setting.site_id == site_id
    assert created_setting.name == name
    assert created_setting.value == value1

    updated_setting = settings_service \
        .create_or_update_setting(site_id, name, value2)

    assert updated_setting is not None
    assert updated_setting.site_id == site_id
    assert updated_setting.name == name
    assert updated_setting.value == value2

def test_find(app):
    site_id = app.site_id
    name = 'name'
    value = 'value'

    setting_before_create = settings_service.find_setting(site_id, name)
    assert setting_before_create is None

    settings_service.create_setting(site_id, name, value)

    setting_after_create = settings_service.find_setting(site_id, name)
    assert setting_after_create is not None
    assert setting_after_create.site_id == site_id
    assert setting_after_create.name == name
    assert setting_after_create.value == value

def test_find_value(app):
    site_id = app.site_id
    name = 'name'
    value = 'value'

    value_before_create = settings_service.find_setting_value(site_id, name)
    assert value_before_create is None

    settings_service.create_setting(site_id, name, value)

    value_after_create = settings_service.find_setting_value(site_id, name)
    assert value_after_create == value

def test_get_settings(app):
    site_id = app.site_id

    all_settings_before_create = settings_service.get_settings(site_id)
    assert all_settings_before_create == set()

    for name, value in {
        ('name1', 'value1'),
        ('name2', 'value2'),
        ('name3', 'value3'),
    }:
        settings_service.create_setting(site_id, name, value)

    all_settings_after_create = settings_service.get_settings(site_id)
    assert all_settings_after_create == {
        SiteSetting(site_id, 'name1', 'value1'),
        SiteSetting(site_id, 'name2', 'value2'),
        SiteSetting(site_id, 'name3', 'value3'),
    }
