"""
byceps.services.site.settings_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from typing import Optional

from ...database import db, upsert
from ...typing import PartyID

from .dbmodels.setting import Setting as DbSetting
from .transfer.models import SiteID, SiteSetting


def create_setting(site_id: SiteID, name: str, value: str) -> SiteSetting:
    """Create a setting for that site."""
    setting = DbSetting(site_id, name, value)

    db.session.add(setting)
    db.session.commit()

    return _db_entity_to_site_setting(setting)


def create_or_update_setting(
    site_id: SiteID, name: str, value: str
) -> SiteSetting:
    """Create or update a setting for that site, depending on whether
    it already exists or not.
    """
    table = DbSetting.__table__
    identifier = {
        'site_id': site_id,
        'name': name,
    }
    replacement = {
        'value': value,
    }

    upsert(table, identifier, replacement)

    return find_setting(site_id, name)


def remove_setting(site_id: SiteID, name: str) -> None:
    """Remove the setting for that site and with that name.

    Do nothing if no setting with that name exists for the site.
    """
    db.session.query(DbSetting) \
        .filter_by(site_id=site_id, name=name) \
        .delete()
    db.session.commit()


def find_setting(site_id: SiteID, name: str) -> Optional[SiteSetting]:
    """Return the setting for that site and with that name, or `None`
    if not found.
    """
    setting = db.session.get(DbSetting, (site_id, name))

    if setting is None:
        return None

    return _db_entity_to_site_setting(setting)


def find_setting_value(site_id: SiteID, name: str) -> Optional[str]:
    """Return the value of the setting for that site and with that
    name, or `None` if not found.
    """
    setting = find_setting(site_id, name)

    if setting is None:
        return None

    return setting.value


def get_settings(site_id: SiteID) -> set[SiteSetting]:
    """Return all settings for that site."""
    settings = db.session \
        .query(DbSetting) \
        .filter_by(site_id=site_id) \
        .all()

    return {_db_entity_to_site_setting(setting) for setting in settings}


def _db_entity_to_site_setting(setting: DbSetting) -> SiteSetting:
    return SiteSetting(
        setting.site_id,
        setting.name,
        setting.value,
    )
