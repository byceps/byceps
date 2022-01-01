"""
byceps.services.news.channel_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from typing import Optional, Sequence

from ...database import db
from ...typing import BrandID

from ..brand import service as brand_service

from .dbmodels.channel import Channel as DbChannel
from .transfer.models import Channel, ChannelID


def create_channel(
    brand_id: BrandID, channel_id: ChannelID, url_prefix: str
) -> Channel:
    """Create a channel for that brand."""
    brand = brand_service.find_brand(brand_id)
    if brand is None:
        raise ValueError(f'Unknown brand ID "{brand_id}"')

    channel = DbChannel(channel_id, brand.id, url_prefix)

    db.session.add(channel)
    db.session.commit()

    return _db_entity_to_channel(channel)


def delete_channel(channel_id: ChannelID) -> None:
    """Delete a news channel."""
    db.session.query(DbChannel) \
        .filter_by(id=channel_id) \
        .delete()

    db.session.commit()


def _find_db_channel(channel_id: ChannelID) -> Optional[DbChannel]:
    return db.session.get(DbChannel, channel_id)


def get_db_channel(channel_id: ChannelID) -> DbChannel:
    channel = _find_db_channel(channel_id)

    if channel is None:
        raise ValueError(f'Unknown channel ID "{channel_id}"')

    return channel


def find_channel(channel_id: ChannelID) -> Optional[Channel]:
    """Return the channel with that id, or `None` if not found."""
    channel = _find_db_channel(channel_id)

    if channel is None:
        return None

    return _db_entity_to_channel(channel)


def get_channel(channel_id: ChannelID) -> Channel:
    """Return the channel with that id, or raise an exception."""
    channel = get_db_channel(channel_id)
    return _db_entity_to_channel(channel)


def get_channels(channel_ids: set[ChannelID]) -> set[Channel]:
    """Return these channels."""
    channels = db.session \
        .query(DbChannel) \
        .filter(DbChannel.id.in_(channel_ids)) \
        .all()

    return {_db_entity_to_channel(channel) for channel in channels}


def get_all_channels() -> list[Channel]:
    """Return all channels."""
    channels = db.session.query(DbChannel).all()

    return [_db_entity_to_channel(channel) for channel in channels]


def get_channels_for_brand(brand_id: BrandID) -> Sequence[Channel]:
    """Return all channels that belong to the brand."""
    channels = db.session \
        .query(DbChannel) \
        .filter_by(brand_id=brand_id) \
        .order_by(DbChannel.id) \
        .all()

    return [_db_entity_to_channel(channel) for channel in channels]


def _db_entity_to_channel(channel: DbChannel) -> Channel:
    return Channel(
        channel.id,
        channel.brand_id,
        channel.url_prefix,
    )
