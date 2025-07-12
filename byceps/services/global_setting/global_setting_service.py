"""
byceps.services.global_setting.global_setting_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from sqlalchemy import delete, select

from byceps.database import db, upsert

from .dbmodels import DbGlobalSetting
from .models import GlobalSetting


def create_setting(name: str, value: str) -> GlobalSetting:
    """Create a global setting."""
    db_setting = DbGlobalSetting(name, value)

    db.session.add(db_setting)
    db.session.commit()

    return _db_entity_to_global_setting(db_setting)


def create_or_update_setting(name: str, value: str) -> GlobalSetting:
    """Create or update a global setting, depending on whether it
    already exists or not.
    """
    table = DbGlobalSetting.__table__
    identifier = {'name': name}
    replacement = {'value': value}

    upsert(table, identifier, replacement)

    return find_setting(name)


def remove_setting(name: str) -> None:
    """Remove the global setting with that name.

    Do nothing if no global setting with that name exists.
    """
    db.session.execute(
        delete(DbGlobalSetting).where(DbGlobalSetting.name == name)
    )
    db.session.commit()


def find_setting(name: str) -> GlobalSetting | None:
    """Return the global setting with that name, or `None` if not found."""
    db_setting = db.session.get(DbGlobalSetting, name)

    if db_setting is None:
        return None

    return _db_entity_to_global_setting(db_setting)


def find_setting_value(name: str) -> str | None:
    """Return the value of the global setting with that name, or `None`
    if not found.
    """
    setting = find_setting(name)

    if setting is None:
        return None

    return setting.value


def get_settings() -> set[GlobalSetting]:
    """Return all global settings."""
    db_settings = db.session.scalars(select(DbGlobalSetting)).all()

    return {
        _db_entity_to_global_setting(db_setting) for db_setting in db_settings
    }


def _db_entity_to_global_setting(db_setting: DbGlobalSetting) -> GlobalSetting:
    return GlobalSetting(
        name=db_setting.name,
        value=db_setting.value,
    )
