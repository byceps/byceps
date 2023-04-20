"""
byceps.services.party.party_setting_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations


from sqlalchemy import delete, select

from byceps.database import db, upsert
from byceps.typing import PartyID

from .dbmodels.setting import DbSetting
from .models import PartySetting


def create_setting(party_id: PartyID, name: str, value: str) -> PartySetting:
    """Create a setting for that party."""
    db_setting = DbSetting(party_id, name, value)

    db.session.add(db_setting)
    db.session.commit()

    return _db_entity_to_party_setting(db_setting)


def create_or_update_setting(
    party_id: PartyID, name: str, value: str
) -> PartySetting:
    """Create or update a setting for that party, depending on whether
    it already exists or not.
    """
    table = DbSetting.__table__
    identifier = {
        'party_id': party_id,
        'name': name,
    }
    replacement = {
        'value': value,
    }

    upsert(table, identifier, replacement)

    return find_setting(party_id, name)


def remove_setting(party_id: PartyID, name: str) -> None:
    """Remove the setting for that party and with that name.

    Do nothing if no setting with that name exists for the party.
    """
    db.session.execute(
        delete(DbSetting)
        .where(DbSetting.party_id == party_id)
        .where(DbSetting.name == name)
    )
    db.session.commit()


def find_setting(party_id: PartyID, name: str) -> PartySetting | None:
    """Return the setting for that party and with that name, or `None`
    if not found.
    """
    db_setting = db.session.get(DbSetting, (party_id, name))

    if db_setting is None:
        return None

    return _db_entity_to_party_setting(db_setting)


def find_setting_value(party_id: PartyID, name: str) -> str | None:
    """Return the value of the setting for that party and with that
    name, or `None` if not found.
    """
    setting = find_setting(party_id, name)

    if setting is None:
        return None

    return setting.value


def get_settings(party_id: PartyID) -> set[PartySetting]:
    """Return all settings for that party."""
    db_settings = db.session.scalars(
        select(DbSetting).filter_by(party_id=party_id)
    ).all()

    return {
        _db_entity_to_party_setting(db_setting) for db_setting in db_settings
    }


def _db_entity_to_party_setting(db_setting: DbSetting) -> PartySetting:
    return PartySetting(
        db_setting.party_id,
        db_setting.name,
        db_setting.value,
    )
