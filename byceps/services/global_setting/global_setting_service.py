"""
byceps.services.global_setting.global_setting_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Optional

from sqlalchemy import delete, select

from ...database import db, upsert

from .dbmodels import DbSetting
from .transfer.models import GlobalSetting


def create_setting(name: str, value: str) -> GlobalSetting:
    """Create a global setting."""
    setting = DbSetting(name, value)

    db.session.add(setting)
    db.session.commit()

    return _db_entity_to_global_setting(setting)


def create_or_update_setting(name: str, value: str) -> GlobalSetting:
    """Create or update a global setting, depending on whether it
    already exists or not.
    """
    table = DbSetting.__table__
    identifier = {'name': name}
    replacement = {'value': value}

    upsert(table, identifier, replacement)

    return find_setting(name)


def remove_setting(name: str) -> None:
    """Remove the global setting with that name.

    Do nothing if no global setting with that name exists.
    """
    db.session.execute(delete(DbSetting).where(DbSetting.name == name))
    db.session.commit()


def find_setting(name: str) -> Optional[GlobalSetting]:
    """Return the global setting with that name, or `None` if not found."""
    setting = db.session.get(DbSetting, name)

    if setting is None:
        return None

    return _db_entity_to_global_setting(setting)


def find_setting_value(name: str) -> Optional[str]:
    """Return the value of the global setting with that name, or `None`
    if not found.
    """
    setting = find_setting(name)

    if setting is None:
        return None

    return setting.value


def get_settings() -> set[GlobalSetting]:
    """Return all global settings."""
    settings = db.session.scalars(select(DbSetting)).all()

    return {_db_entity_to_global_setting(setting) for setting in settings}


def _db_entity_to_global_setting(setting: DbSetting) -> GlobalSetting:
    return GlobalSetting(
        setting.name,
        setting.value,
    )
