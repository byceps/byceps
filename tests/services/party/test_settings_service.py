"""
:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.services.party import settings_service as service
from byceps.services.party.transfer.models import PartySetting

from tests.base import AbstractAppTestCase


class PartySettingsServiceTest(AbstractAppTestCase):

    def setUp(self):
        super().setUp()

        self.create_brand_and_party()

    def test_create(self):
        party_id = self.party.id
        name = 'name'
        value = 'value'

        assert service.find_setting(party_id, name) is None

        setting = service.create_setting(party_id, name, value)

        assert setting is not None
        assert setting.party_id == party_id
        assert setting.name == name
        assert setting.value == value

    def test_create_or_update(self):
        party_id = self.party.id
        name = 'name'
        value1 = 'value1'
        value2 = 'value2'

        assert service.find_setting(party_id, name) is None

        created_setting = service.create_or_update_setting(party_id, name, value1)

        assert created_setting is not None
        assert created_setting.party_id == party_id
        assert created_setting.name == name
        assert created_setting.value == value1

        updated_setting = service.create_or_update_setting(party_id, name, value2)

        assert updated_setting is not None
        assert updated_setting.party_id == party_id
        assert updated_setting.name == name
        assert updated_setting.value == value2

    def test_find(self):
        party_id = self.party.id
        name = 'name'
        value = 'value'

        setting_before_create = service.find_setting(party_id, name)
        assert setting_before_create is None

        service.create_setting(party_id, name, value)

        setting_after_create = service.find_setting(party_id, name)
        assert setting_after_create is not None
        assert setting_after_create.party_id == party_id
        assert setting_after_create.name == name
        assert setting_after_create.value == value

    def test_find_value(self):
        party_id = self.party.id
        name = 'name'
        value = 'value'

        value_before_create = service.find_setting_value(party_id, name)
        assert value_before_create is None

        service.create_setting(party_id, name, value)

        value_after_create = service.find_setting_value(party_id, name)
        assert value_after_create == value

    def test_get_settings(self):
        party_id = self.party.id

        all_settings_before_create = service.get_settings(party_id)
        assert all_settings_before_create == set()

        for name, value in {
            ('name1', 'value1'),
            ('name2', 'value2'),
            ('name3', 'value3'),
        }:
            service.create_setting(party_id, name, value)

        all_settings_after_create = service.get_settings(party_id)
        assert all_settings_after_create == {
            PartySetting(party_id, 'name1', 'value1'),
            PartySetting(party_id, 'name2', 'value2'),
            PartySetting(party_id, 'name3', 'value3'),
        }
