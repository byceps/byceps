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
        name = 'create-name'
        value = 'create-value'

        assert service.find_setting(party_id, name) is None

        setting = service.create_setting(party_id, name, value)

        assert setting is not None
        assert setting.party_id == party_id
        assert setting.name == name
        assert setting.value == value

    def test_find(self):
        party_id = self.party.id
        name = 'find-name'
        value = 'find-value'

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
        name = 'find_value-name'
        value = 'find_value-value'

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
            ('key1', 'value1'),
            ('key2', 'value2'),
            ('key3', 'value3'),
        }:
            service.create_setting(party_id, name, value)

        all_settings_after_create = service.get_settings(party_id)
        assert all_settings_after_create == {
            PartySetting(party_id, 'key1', 'value1'),
            PartySetting(party_id, 'key2', 'value2'),
            PartySetting(party_id, 'key3', 'value3'),
        }
