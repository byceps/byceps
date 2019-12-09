"""
byceps.services.site.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import List, Optional

from ...database import db
from ...typing import PartyID

from .models.site import Site as DbSite
from .transfer.models import Site, SiteID


class UnknownSiteId(Exception):
    pass


def create_site(
    site_id: SiteID,
    title: str,
    server_name: str,
    email_config_id: str,
    enabled: bool,
    user_account_creation_enabled: bool,
    login_enabled: bool,
    *,
    party_id: Optional[PartyID] = None,
) -> Site:
    """Create a site for that party."""
    site = DbSite(
        site_id,
        title,
        server_name,
        email_config_id,
        enabled,
        user_account_creation_enabled,
        login_enabled,
        party_id=party_id,
    )

    db.session.add(site)
    db.session.commit()

    return _db_entity_to_site(site)


def update_site(
    site_id: SiteID,
    title: str,
    server_name: str,
    email_config_id: str,
    party_id: Optional[PartyID],
    enabled: bool,
    user_account_creation_enabled: bool,
    login_enabled: bool,
) -> Site:
    """Update the site."""
    site = DbSite.query.get(site_id)

    if site is None:
        raise UnknownSiteId(site_id)

    site.title = title
    site.server_name = server_name
    site.email_config_id = email_config_id
    site.party_id = party_id
    site.enabled = enabled
    site.user_account_creation_enabled = user_account_creation_enabled
    site.login_enabled = login_enabled

    db.session.commit()

    return _db_entity_to_site(site)


def find_site(site_id: SiteID) -> Optional[Site]:
    """Return the site with that ID, or `None` if not found."""
    site = DbSite.query.get(site_id)

    if site is None:
        return None

    return _db_entity_to_site(site)


def get_site(site_id: SiteID) -> Site:
    """Return the site with that ID."""
    site = find_site(site_id)

    if site is None:
        raise UnknownSiteId(site_id)

    return site


def get_all_sites() -> List[Site]:
    """Return all sites."""
    sites = DbSite.query.all()

    return [_db_entity_to_site(site) for site in sites]


def get_enabled_sites() -> List[Site]:
    """Return all enabled sites."""
    sites = DbSite.query \
        .filter_by(enabled=True) \
        .all()

    return [_db_entity_to_site(site) for site in sites]


def _db_entity_to_site(site: DbSite) -> Site:
    return Site(
        site.id,
        site.title,
        site.server_name,
        site.email_config_id,
        site.party_id,
        site.enabled,
        site.user_account_creation_enabled,
        site.login_enabled,
    )
