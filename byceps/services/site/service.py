"""
byceps.services.site.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
import dataclasses
from typing import Optional, Union

from ...database import db
from ...typing import BrandID, PartyID

from ..board.transfer.models import BoardID
from ..brand import service as brand_service
from ..news import channel_service as news_channel_service
from ..news.transfer.models import ChannelID as NewsChannelID
from ..shop.storefront.transfer.models import StorefrontID

from .dbmodels.site import Site as DbSite
from .dbmodels.setting import Setting as DbSetting
from .transfer.models import Site, SiteID, SiteWithBrand


class UnknownSiteId(Exception):
    pass


def create_site(
    site_id: SiteID,
    title: str,
    server_name: str,
    brand_id: BrandID,
    *,
    enabled: bool = False,
    user_account_creation_enabled: bool = False,
    login_enabled: bool = False,
    party_id: Optional[PartyID] = None,
    board_id: Optional[BoardID] = None,
    storefront_id: Optional[StorefrontID] = None,
) -> Site:
    """Create a site for that party."""
    site = DbSite(
        site_id,
        title,
        server_name,
        brand_id,
        enabled,
        user_account_creation_enabled,
        login_enabled,
        party_id=party_id,
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
    party_id: Optional[PartyID],
    enabled: bool,
    user_account_creation_enabled: bool,
    login_enabled: bool,
    board_id: Optional[BoardID],
    storefront_id: Optional[StorefrontID],
    archived: bool,
) -> Site:
    """Update the site."""
    site = _get_db_site(site_id)

    site.title = title
    site.server_name = server_name
    site.brand_id = brand_id
    site.party_id = party_id
    site.enabled = enabled
    site.user_account_creation_enabled = user_account_creation_enabled
    site.login_enabled = login_enabled
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


def _find_db_site(site_id: SiteID) -> Optional[DbSite]:
    return DbSite.query.get(site_id)


def _get_db_site(site_id: SiteID) -> DbSite:
    site = _find_db_site(site_id)

    if site is None:
        raise UnknownSiteId(site_id)

    return site


def find_site(site_id: SiteID) -> Optional[Site]:
    """Return the site with that ID, or `None` if not found."""
    site = _find_db_site(site_id)

    if site is None:
        return None

    return _db_entity_to_site(site)


def get_site(site_id: SiteID) -> Site:
    """Return the site with that ID."""
    site = _get_db_site(site_id)
    return _db_entity_to_site(site)


def get_all_sites() -> set[Site]:
    """Return all sites."""
    sites = DbSite.query.all()

    return {_db_entity_to_site(site) for site in sites}


def get_sites_for_brand(brand_id: BrandID) -> set[Site]:
    """Return the sites for that brand."""
    sites = DbSite.query \
        .filter_by(brand_id=brand_id) \
        .all()

    return {_db_entity_to_site(site) for site in sites}


def get_current_sites(
    brand_id: Optional[BrandID] = None, *, include_brands: bool = False
) -> set[Union[Site, SiteWithBrand]]:
    """Return all "current" (i.e. enabled and not archived) sites."""
    query = DbSite.query

    if brand_id is not None:
        query = query.filter_by(brand_id=brand_id)

    if include_brands:
        query = query.options(db.joinedload(DbSite.brand))

    sites = query \
        .filter_by(enabled=True) \
        .filter_by(archived=False) \
        .all()

    if include_brands:
        transform = _db_entity_to_site_with_brand
    else:
        transform = _db_entity_to_site

    return {transform(site) for site in sites}


def _db_entity_to_site(site: DbSite) -> Site:
    news_channel_ids = frozenset(channel.id for channel in site.news_channels)

    return Site(
        id=site.id,
        title=site.title,
        server_name=site.server_name,
        brand_id=site.brand_id,
        party_id=site.party_id,
        enabled=site.enabled,
        user_account_creation_enabled=site.user_account_creation_enabled,
        login_enabled=site.login_enabled,
        news_channel_ids=news_channel_ids,
        board_id=site.board_id,
        storefront_id=site.storefront_id,
        archived=site.archived,
    )


def _db_entity_to_site_with_brand(site_entity: DbSite) -> SiteWithBrand:
    site = _db_entity_to_site(site_entity)
    brand = brand_service._db_entity_to_brand(site_entity.brand)

    site_tuple = dataclasses.astuple(site)
    brand_tuple = (brand,)

    return SiteWithBrand(*(site_tuple + brand_tuple))


def add_news_channel(site_id: SiteID, news_channel_id: NewsChannelID) -> None:
    """Add the news channel to the site."""
    site = _get_db_site(site_id)
    news_channel = news_channel_service.get_db_channel(news_channel_id)

    site.news_channels.append(news_channel)
    db.session.commit()


def remove_news_channel(
    site_id: SiteID, news_channel_id: NewsChannelID
) -> None:
    """Remove the news channel from the site."""
    site = _get_db_site(site_id)
    news_channel = news_channel_service.get_db_channel(news_channel_id)

    site.news_channels.remove(news_channel)
    db.session.commit()
