"""
byceps.services.party.settings_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import Optional

from ...typing import PartyID

from .models.setting import Setting as DbSetting
from .transfer.models import PartySetting


def find_setting(party_id: PartyID, name: str) -> Optional[PartySetting]:
    """Return the setting for that party and with that name, or `None`
    if not found.
    """
    setting = DbSetting.query.get((party_id, name))

    if setting is None:
        return None

    return _db_entity_to_party_setting(setting)


def _db_entity_to_party_setting(setting: DbSetting) -> PartySetting:
    return PartySetting(
        setting.party_id,
        setting.name,
        setting.value,
    )
