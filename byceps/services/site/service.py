"""
byceps.services.site.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import dataclasses
from typing import List, Optional, Union

from ...database import db
from ...typing import BrandID, PartyID

from ..board.transfer.models import BoardID
from ..brand import service as brand_service
from ..news.transfer.models import ChannelID as NewsChannelID
from ..shop.storefront.transfer.models import StorefrontID

from .models.site import Site as DbSite
from .models.setting import Setting as DbSetting
from .transfer.models import Site, SiteID, SiteWithBrand


class UnknownSiteId(Exception):
    pass


def create_site(
    site_id: SiteID,
    title: str,
    server_name: str,
    brand_id: BrandID,
    email_config_id: str,
    *,
    enabled: bool = False,
    user_account_creation_enabled: bool = False,
    login_enabled: bool = False,
    party_id: Optional[PartyID] = None,
    news_channel_id: Optional[NewsChannelID] = None,
    board_id: Optional[BoardID] = None,
    storefront_id: Optional[StorefrontID] = None,
) -> Site:
    """Create a site for that party."""
    site = DbSite(
        site_id,
        title,
        server_name,
        brand_id,
        email_config_id,
        enabled,
        user_account_creation_enabled,
        login_enabled,
        party_id=party_id,
        news_channel_id=news_channel_id,
        board_id=board_id,
        storefront_id=storefront_id,
    )

    db.session.add(site)
    db.session.commit()

    return _db_entity_to_site(site)


def update_site(
    site_id: SiteID,
    title: str,
    server_name: str,
    brand_id: BrandID,
    email_config_id: str,
    party_id: Optional[PartyID],
    enabled: bool,
    user_account_creation_enabled: bool,
    login_enabled: bool,
    news_channel_id: Optional[NewsChannelID],
    board_id: Optional[BoardID],
    storefront_id: Optional[StorefrontID],
    archived: bool,
) -> Site:
    """Update the site."""
    site = DbSite.query.get(site_id)

    if site is None:
        raise UnknownSiteId(site_id)

    site.title = title
    site.server_name = server_name
    site.brand_id = brand_id
    site.email_config_id = email_config_id
    site.party_id = party_id
    site.enabled = enabled
    site.user_account_creation_enabled = user_account_creation_enabled
    site.login_enabled = login_enabled
    site.news_channel_id = news_channel_id
    site.board_id = board_id
    site.storefront_id = storefront_id
    site.archived = archived

    db.session.commit()

    return _db_entity_to_site(site)


def delete_site(site_id: SiteID) -> None:
    """Delete a site."""
    db.session.query(DbSetting) \
        .filter_by(site_id=site_id) \
        .delete()

    db.session.query(DbSite) \
        .filter_by(id=site_id) \
        .delete()

    db.session.commit()


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


def get_sites_for_brand(brand_id: BrandID) -> List[Site]:
    """Return the sites for that brand."""
    sites = DbSite.query \
        .filter_by(brand_id=brand_id) \
        .all()

    return [_db_entity_to_site(site) for site in sites]


def get_current_sites(*, include_brands: bool = True) -> List[Union[Site, SiteWithBrand]]:
    """Return all "current" (i.e. enabled and not archived) sites."""
    query = DbSite.query

    if include_brands:
        query = query.options(db.joinedload('brand'))

    sites = query \
        .filter_by(enabled=True) \
        .filter_by(archived=False) \
        .all()

    if include_brands:
        transform = _db_entity_to_site_with_brand
    else:
        transform = _db_entity_to_site

    return [transform(site) for site in sites]


def _db_entity_to_site(site: DbSite) -> Site:
    return Site(
        site.id,
        site.title,
        site.server_name,
        site.brand_id,
        site.email_config_id,
        site.party_id,
        site.enabled,
        site.user_account_creation_enabled,
        site.login_enabled,
        site.news_channel_id,
        site.board_id,
        site.storefront_id,
        site.archived,
    )


def _db_entity_to_site_with_brand(site_entity: DbSite) -> SiteWithBrand:
    site = _db_entity_to_site(site_entity)
    brand = brand_service._db_entity_to_brand(site_entity.brand)

    return SiteWithBrand(*dataclasses.astuple(site), brand=brand)
