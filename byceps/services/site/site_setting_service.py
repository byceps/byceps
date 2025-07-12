"""
byceps.services.site.site_setting_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from sqlalchemy import delete, select

from byceps.database import db, upsert

from .dbmodels import DbSiteSetting
from .models import SiteID, SiteSetting


def create_setting(site_id: SiteID, name: str, value: str) -> SiteSetting:
    """Create a setting for that site."""
    db_setting = DbSiteSetting(site_id, name, value)

    db.session.add(db_setting)
    db.session.commit()

    return _db_entity_to_site_setting(db_setting)


def create_or_update_setting(
    site_id: SiteID, name: str, value: str
) -> SiteSetting:
    """Create or update a setting for that site, depending on whether
    it already exists or not.
    """
    table = DbSiteSetting.__table__
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
    db.session.execute(
        delete(DbSiteSetting)
        .where(DbSiteSetting.site_id == site_id)
        .where(DbSiteSetting.name == name)
    )
    db.session.commit()


def find_setting(site_id: SiteID, name: str) -> SiteSetting | None:
    """Return the setting for that site and with that name, or `None`
    if not found.
    """
    db_setting = db.session.get(DbSiteSetting, (site_id, name))

    if db_setting is None:
        return None

    return _db_entity_to_site_setting(db_setting)


def find_setting_value(site_id: SiteID, name: str) -> str | None:
    """Return the value of the setting for that site and with that
    name, or `None` if not found.
    """
    setting = find_setting(site_id, name)

    if setting is None:
        return None

    return setting.value


def get_settings(site_id: SiteID) -> set[SiteSetting]:
    """Return all settings for that site."""
    db_settings = db.session.scalars(
        select(DbSiteSetting).filter_by(site_id=site_id)
    ).all()

    return {
        _db_entity_to_site_setting(db_setting) for db_setting in db_settings
    }


def _db_entity_to_site_setting(db_setting: DbSiteSetting) -> SiteSetting:
    return SiteSetting(
        site_id=db_setting.site_id,
        name=db_setting.name,
        value=db_setting.value,
    )
