"""
byceps.services.brand.brand_setting_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from sqlalchemy import delete, select

from byceps.database import db, upsert
from byceps.services.brand.models import BrandID

from .dbmodels import DbBrandSetting
from .models import BrandSetting


def create_setting(brand_id: BrandID, name: str, value: str) -> BrandSetting:
    """Create a setting for that brand."""
    db_setting = DbBrandSetting(brand_id, name, value)

    db.session.add(db_setting)
    db.session.commit()

    return _db_entity_to_brand_setting(db_setting)


def create_or_update_setting(
    brand_id: BrandID, name: str, value: str
) -> BrandSetting:
    """Create or update a setting for that brand, depending on whether
    it already exists or not.
    """
    table = DbBrandSetting.__table__
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
        delete(DbBrandSetting)
        .where(DbBrandSetting.brand_id == brand_id)
        .where(DbBrandSetting.name == name)
    )
    db.session.commit()


def find_setting(brand_id: BrandID, name: str) -> BrandSetting | None:
    """Return the setting for that brand and with that name, or `None`
    if not found.
    """
    db_setting = db.session.get(DbBrandSetting, (brand_id, name))

    if db_setting is None:
        return None

    return _db_entity_to_brand_setting(db_setting)


def find_setting_value(brand_id: BrandID, name: str) -> str | None:
    """Return the value of the setting for that brand and with that
    name, or `None` if not found.
    """
    db_setting = find_setting(brand_id, name)

    if db_setting is None:
        return None

    return db_setting.value


def get_settings(brand_id: BrandID) -> set[BrandSetting]:
    """Return all settings for that brand."""
    db_settings = db.session.scalars(
        select(DbBrandSetting).filter_by(brand_id=brand_id)
    ).all()

    return {
        _db_entity_to_brand_setting(db_setting) for db_setting in db_settings
    }


def _db_entity_to_brand_setting(db_setting: DbBrandSetting) -> BrandSetting:
    return BrandSetting(
        db_setting.brand_id,
        db_setting.name,
        db_setting.value,
    )
