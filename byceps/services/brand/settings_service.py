"""
byceps.services.brand.settings_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import Optional

from ...database import db
from ...typing import BrandID

from .models.setting import Setting as DbSetting
from .transfer.models import BrandSetting


def create_setting(brand_id: BrandID, name: str, value: str) -> BrandSetting:
    """Create a setting for that brand."""
    setting = DbSetting(brand_id, name, value)

    db.session.add(setting)
    db.session.commit()

    return _db_entity_to_brand_setting(setting)


def find_setting(brand_id: BrandID, name: str) -> Optional[BrandSetting]:
    """Return the setting for that brand and with that name, or `None`
    if not found.
    """
    setting = DbSetting.query.get((brand_id, name))

    if setting is None:
        return None

    return _db_entity_to_brand_setting(setting)


def find_setting_value(brand_id: BrandID, name: str) -> Optional[str]:
    """Return the value of the setting for that brand and with that
    name, or `None` if not found.
    """
    setting = find_setting(brand_id, name)

    if setting is None:
        return None

    return setting.value


def _db_entity_to_brand_setting(setting: DbSetting) -> BrandSetting:
    return BrandSetting(
        setting.brand_id,
        setting.name,
        setting.value,
    )
