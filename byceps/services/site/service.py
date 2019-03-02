"""
byceps.services.site.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import List, Optional

from ...typing import PartyID

from .models.site import Site as DbSite
from .transfer.models import Site, SiteID


def find_site(site_id: SiteID) -> Optional[Site]:
    """Return the site with that id, or `None` if not found."""
    site = DbSite.query.get(site_id)

    if site is None:
        return None

    return _db_entity_to_site(site)


def get_all_sites() -> List[Site]:
    """Return all sites."""
    sites = DbSite.query.all()

    return [_db_entity_to_site(site) for site in sites]


def _db_entity_to_site(site: DbSite) -> Site:
    return Site(
        site.id,
        site.party_id,
        site.title,
    )
