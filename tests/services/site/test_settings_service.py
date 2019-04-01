"""
:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.services.site import settings_service as service
from byceps.services.site.transfer.models import SiteSetting

from tests.base import AbstractAppTestCase


class SiteSettingsServiceTest(AbstractAppTestCase):

    def setUp(self):
        super().setUp()

        self.create_brand_and_party()
        self.site = self.create_site()

    def test_create(self):
        site_id = self.site.id
        name = 'name'
        value = 'value'

        assert service.find_setting(site_id, name) is None

        setting = service.create_setting(site_id, name, value)

        assert setting is not None
        assert setting.site_id == site_id
        assert setting.name == name
        assert setting.value == value

    def test_find(self):
        site_id = self.site.id
        name = 'name'
        value = 'value'

        setting_before_create = service.find_setting(site_id, name)
        assert setting_before_create is None

        service.create_setting(site_id, name, value)

        setting_after_create = service.find_setting(site_id, name)
        assert setting_after_create is not None
        assert setting_after_create.site_id == site_id
        assert setting_after_create.name == name
        assert setting_after_create.value == value

    def test_find_value(self):
        site_id = self.site.id
        name = 'name'
        value = 'value'

        value_before_create = service.find_setting_value(site_id, name)
        assert value_before_create is None

        service.create_setting(site_id, name, value)

        value_after_create = service.find_setting_value(site_id, name)
        assert value_after_create == value

    def test_get_settings(self):
        site_id = self.site.id

        all_settings_before_create = service.get_settings(site_id)
        assert all_settings_before_create == set()

        for name, value in {
            ('name1', 'value1'),
            ('name2', 'value2'),
            ('name3', 'value3'),
        }:
            service.create_setting(site_id, name, value)

        all_settings_after_create = service.get_settings(site_id)
        assert all_settings_after_create == {
            SiteSetting(site_id, 'name1', 'value1'),
            SiteSetting(site_id, 'name2', 'value2'),
            SiteSetting(site_id, 'name3', 'value3'),
        }
