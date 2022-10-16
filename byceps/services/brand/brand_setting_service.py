"""
byceps.services.brand.brand_setting_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Optional

from sqlalchemy import delete, select

from ...database import db, upsert
from ...typing import BrandID

from .dbmodels.setting import DbSetting
from .transfer.models import BrandSetting


def create_setting(brand_id: BrandID, name: str, value: str) -> BrandSetting:
    """Create a setting for that brand."""
    setting = DbSetting(brand_id, name, value)

    db.session.add(setting)
    db.session.commit()

    return _db_entity_to_brand_setting(setting)


def create_or_update_setting(
    brand_id: BrandID, name: str, value: str
) -> BrandSetting:
    """Create or update a setting for that brand, depending on whether
    it already exists or not.
    """
    table = DbSetting.__table__
    identifier = {
        'brand_id': brand_id,
        'name': name,
    }
    replacement = {
        'value': value,
    }

    upsert(table, identifier, replacement)

    return find_setting(brand_id, name)


def remove_setting(brand_id: BrandID, name: str) -> None:
    """Remove the setting for that brand and with that name.

    Do nothing if no setting with that name exists for the brand.
    """
    db.session.execute(
        delete(DbSetting)
        .where(DbSetting.brand_id == brand_id)
        .where(DbSetting.name == name)
    )
    db.session.commit()


def find_setting(brand_id: BrandID, name: str) -> Optional[BrandSetting]:
    """Return the setting for that brand and with that name, or `None`
    if not found.
    """
    setting = db.session.get(DbSetting, (brand_id, name))

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


def get_settings(brand_id: BrandID) -> set[BrandSetting]:
    """Return all settings for that brand."""
    settings = db.session.scalars(
        select(DbSetting).filter_by(brand_id=brand_id)
    ).all()

    return {_db_entity_to_brand_setting(setting) for setting in settings}


def _db_entity_to_brand_setting(setting: DbSetting) -> BrandSetting:
    return BrandSetting(
        setting.brand_id,
        setting.name,
        setting.value,
    )
