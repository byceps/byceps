"""
:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import pytest

from byceps.services.site.models.setting import Setting as DbSetting
from byceps.services.site import settings_service
from byceps.services.site.transfer.models import SiteSetting

from tests.helpers import create_email_config, create_site

from ...conftest import database_recreated


@pytest.fixture(scope='module')
def app(party_app, db):
    with party_app.app_context():
        with database_recreated(db):
            _app = party_app

            create_email_config()

            site = create_site()

            _app.site_id = site.id

            yield _app


def test_create(app):
    site_id = app.site_id
    name = 'name1'
    value = 'value1'

    assert settings_service.find_setting(site_id, name) is None

    setting = settings_service.create_setting(site_id, name, value)

    assert setting is not None
    assert setting.site_id == site_id
    assert setting.name == name
    assert setting.value == value


def test_create_or_update(app):
    site_id = app.site_id
    name = 'name2'
    value1 = 'value2a'
    value2 = 'value2b'

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
    name = 'name3'
    value = 'value3'

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
    name = 'name4'
    value = 'value4'

    value_before_create = settings_service.find_setting_value(site_id, name)
    assert value_before_create is None

    settings_service.create_setting(site_id, name, value)

    value_after_create = settings_service.find_setting_value(site_id, name)
    assert value_after_create == value


def test_get_settings(app):
    site_id = app.site_id

    # Clean up.
    DbSetting.query.delete()

    all_settings_before_create = settings_service.get_settings(site_id)
    assert all_settings_before_create == set()

    for name, value in {
        ('name5a', 'value5a'),
        ('name5b', 'value5b'),
        ('name5c', 'value5c'),
    }:
        settings_service.create_setting(site_id, name, value)

    all_settings_after_create = settings_service.get_settings(site_id)
    assert all_settings_after_create == {
        SiteSetting(site_id, 'name5a', 'value5a'),
        SiteSetting(site_id, 'name5b', 'value5b'),
        SiteSetting(site_id, 'name5c', 'value5c'),
    }
