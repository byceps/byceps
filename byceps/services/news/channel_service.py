"""
byceps.services.news.channel_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import List, Optional, Sequence

from ...database import db
from ...typing import BrandID

from ..brand import service as brand_service

from .models.channel import Channel as DbChannel
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


def find_channel(channel_id: ChannelID) -> Optional[Channel]:
    """Return the channel with that id, or `None` if not found."""
    channel = DbChannel.query.get(channel_id)

    if channel is None:
        return None

    return _db_entity_to_channel(channel)


def get_all_channels() -> List[Channel]:
    """Return all channels."""
    channels = DbChannel.query.all()

    return [_db_entity_to_channel(channel) for channel in channels]


def get_channels_for_brand(brand_id: BrandID) -> Sequence[Channel]:
    """Return all channels that belong to the brand."""
    channels = DbChannel.query \
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
