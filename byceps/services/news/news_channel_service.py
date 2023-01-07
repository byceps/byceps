"""
byceps.services.news.news_channel_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Optional

from sqlalchemy import delete, select

from ...database import db
from ...typing import BrandID

from ..brand import brand_service
from ..site.transfer.models import SiteID

from .dbmodels.channel import DbNewsChannel
from .transfer.models import NewsChannel, NewsChannelID


def create_channel(
    brand_id: BrandID,
    channel_id: NewsChannelID,
    *,
    announcement_site_id: Optional[SiteID] = None,
) -> NewsChannel:
    """Create a channel for that brand."""
    brand = brand_service.find_brand(brand_id)
    if brand is None:
        raise ValueError(f'Unknown brand ID "{brand_id}"')

    db_channel = DbNewsChannel(
        channel_id, brand.id, announcement_site_id=announcement_site_id
    )

    db.session.add(db_channel)
    db.session.commit()

    return _db_entity_to_channel(db_channel)


def update_channel(
    channel_id: NewsChannelID,
    announcement_site_id: Optional[SiteID],
    archived: bool,
) -> NewsChannel:
    """Update a channel."""
    db_channel = get_db_channel(channel_id)

    db_channel.announcement_site_id = announcement_site_id
    db_channel.archived = archived

    db.session.commit()

    return _db_entity_to_channel(db_channel)


def delete_channel(channel_id: NewsChannelID) -> None:
    """Delete a news channel."""
    db.session.execute(
        delete(DbNewsChannel).where(DbNewsChannel.id == channel_id)
    )
    db.session.commit()


def _find_db_channel(channel_id: NewsChannelID) -> Optional[DbNewsChannel]:
    return db.session.get(DbNewsChannel, channel_id)


def get_db_channel(channel_id: NewsChannelID) -> DbNewsChannel:
    db_channel = _find_db_channel(channel_id)

    if db_channel is None:
        raise ValueError(f'Unknown channel ID "{channel_id}"')

    return db_channel


def find_channel(channel_id: NewsChannelID) -> Optional[NewsChannel]:
    """Return the channel with that id, or `None` if not found."""
    db_channel = _find_db_channel(channel_id)

    if db_channel is None:
        return None

    return _db_entity_to_channel(db_channel)


def get_channel(channel_id: NewsChannelID) -> NewsChannel:
    """Return the channel with that id, or raise an exception."""
    db_channel = get_db_channel(channel_id)
    return _db_entity_to_channel(db_channel)


def get_channels(channel_ids: set[NewsChannelID]) -> set[NewsChannel]:
    """Return these channels."""
    db_channels = db.session.scalars(
        select(DbNewsChannel).filter(DbNewsChannel.id.in_(channel_ids))
    ).all()

    return {_db_entity_to_channel(db_channel) for db_channel in db_channels}


def get_all_channels() -> list[NewsChannel]:
    """Return all channels."""
    db_channels = db.session.scalars(select(DbNewsChannel)).all()

    return [_db_entity_to_channel(db_channel) for db_channel in db_channels]


def get_channels_for_brand(brand_id: BrandID) -> list[NewsChannel]:
    """Return all channels that belong to the brand."""
    db_channels = db.session.scalars(
        select(DbNewsChannel)
        .filter_by(brand_id=brand_id)
        .order_by(DbNewsChannel.id)
    ).all()

    return [_db_entity_to_channel(db_channel) for db_channel in db_channels]


def _db_entity_to_channel(db_channel: DbNewsChannel) -> NewsChannel:
    return NewsChannel(
        id=db_channel.id,
        brand_id=db_channel.brand_id,
        announcement_site_id=db_channel.announcement_site_id,
        archived=db_channel.archived,
    )
