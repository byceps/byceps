"""
byceps.services.site.site_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
import dataclasses
from typing import Callable, Optional

from sqlalchemy import select

from ...database import db
from ...typing import BrandID, PartyID

from ..board.models import BoardID
from ..brand import brand_service
from ..news.models import NewsChannelID
from ..news import news_channel_service
from ..shop.storefront.models import StorefrontID

from .dbmodels.site import DbSite
from .dbmodels.setting import DbSetting
from .models import Site, SiteID, SiteWithBrand


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
    db_site = DbSite(
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

    db.session.add(db_site)
    db.session.commit()

    return _db_entity_to_site(db_site)


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
    db_site = _get_db_site(site_id)

    db_site.title = title
    db_site.server_name = server_name
    db_site.brand_id = brand_id
    db_site.party_id = party_id
    db_site.enabled = enabled
    db_site.user_account_creation_enabled = user_account_creation_enabled
    db_site.login_enabled = login_enabled
    db_site.board_id = board_id
    db_site.storefront_id = storefront_id
    db_site.archived = archived

    db.session.commit()

    return _db_entity_to_site(db_site)


def delete_site(site_id: SiteID) -> None:
    """Delete a site."""
    db.session.query(DbSetting).filter_by(site_id=site_id).delete()

    db.session.query(DbSite).filter_by(id=site_id).delete()

    db.session.commit()


def _find_db_site(site_id: SiteID) -> Optional[DbSite]:
    return db.session.get(DbSite, site_id)


def _get_db_site(site_id: SiteID) -> DbSite:
    db_site = _find_db_site(site_id)

    if db_site is None:
        raise UnknownSiteId(site_id)

    return db_site


def find_site(site_id: SiteID) -> Optional[Site]:
    """Return the site with that ID, or `None` if not found."""
    db_site = _find_db_site(site_id)

    if db_site is None:
        return None

    return _db_entity_to_site(db_site)


def get_site(site_id: SiteID) -> Site:
    """Return the site with that ID."""
    db_site = _get_db_site(site_id)
    return _db_entity_to_site(db_site)


def get_all_sites() -> set[Site]:
    """Return all sites."""
    db_sites = db.session.query(DbSite).all()

    return {_db_entity_to_site(db_site) for db_site in db_sites}


def get_sites(site_ids: set[SiteID]) -> list[Site]:
    """Return the sites with those IDs."""
    if not site_ids:
        return []

    db_sites = db.session.scalars(
        select(DbSite).filter(DbSite.id.in_(site_ids))
    ).all()

    return [_db_entity_to_site(db_site) for db_site in db_sites]


def get_sites_for_brand(brand_id: BrandID) -> set[Site]:
    """Return the sites for that brand."""
    db_sites = db.session.query(DbSite).filter_by(brand_id=brand_id).all()

    return {_db_entity_to_site(db_site) for db_site in db_sites}


def get_current_sites(
    brand_id: Optional[BrandID] = None, *, include_brands: bool = False
) -> set[Site | SiteWithBrand]:
    """Return all "current" (i.e. enabled and not archived) sites."""
    query = db.session.query(DbSite)

    if brand_id is not None:
        query = query.filter_by(brand_id=brand_id)

    if include_brands:
        query = query.options(db.joinedload(DbSite.brand))

    db_sites = query.filter_by(enabled=True).filter_by(archived=False).all()

    transform: Callable[[DbSite], Site | SiteWithBrand]
    if include_brands:
        transform = _db_entity_to_site_with_brand
    else:
        transform = _db_entity_to_site

    return {transform(db_site) for db_site in db_sites}


def _db_entity_to_site(db_site: DbSite) -> Site:
    news_channel_ids = frozenset(
        channel.id for channel in db_site.news_channels
    )

    return Site(
        id=db_site.id,
        title=db_site.title,
        server_name=db_site.server_name,
        brand_id=db_site.brand_id,
        party_id=db_site.party_id,
        enabled=db_site.enabled,
        user_account_creation_enabled=db_site.user_account_creation_enabled,
        login_enabled=db_site.login_enabled,
        news_channel_ids=news_channel_ids,
        board_id=db_site.board_id,
        storefront_id=db_site.storefront_id,
        archived=db_site.archived,
    )


def _db_entity_to_site_with_brand(db_site: DbSite) -> SiteWithBrand:
    site = _db_entity_to_site(db_site)
    brand = brand_service._db_entity_to_brand(db_site.brand)

    site_tuple = dataclasses.astuple(site)
    brand_tuple = (brand,)

    return SiteWithBrand(*(site_tuple + brand_tuple))


def add_news_channel(site_id: SiteID, news_channel_id: NewsChannelID) -> None:
    """Add the news channel to the site."""
    db_site = _get_db_site(site_id)
    news_channel = news_channel_service.get_db_channel(news_channel_id)

    db_site.news_channels.append(news_channel)
    db.session.commit()


def remove_news_channel(
    site_id: SiteID, news_channel_id: NewsChannelID
) -> None:
    """Remove the news channel from the site."""
    db_site = _get_db_site(site_id)
    news_channel = news_channel_service.get_db_channel(news_channel_id)

    db_site.news_channels.remove(news_channel)
    db.session.commit()
