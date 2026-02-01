"""
byceps.services.news.news_image_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime
from pathlib import Path
from typing import BinaryIO

from sqlalchemy import select

from byceps.byceps_app import get_current_byceps_app
from byceps.database import db
from byceps.services.user.models import User
from byceps.util import upload
from byceps.util.image.dimensions import determine_dimensions, Dimensions
from byceps.util.image.image_type import determine_image_type, ImageType
from byceps.util.result import Err, Ok, Result
from byceps.util.uuid import generate_uuid7

from .dbmodels import DbNewsImage, DbNewsItem
from .models import NewsChannelID, NewsImage, NewsImageID, NewsItem, NewsItemID


ALLOWED_IMAGE_TYPES = frozenset(
    [
        ImageType.jpeg,
        ImageType.png,
        ImageType.svg,
        ImageType.webp,
    ],
)


MAXIMUM_DIMENSIONS = Dimensions(2560, 1440)


def create_image(
    creator: User,
    item: NewsItem,
    stream: BinaryIO,
    *,
    alt_text: str | None = None,
    caption: str | None = None,
    attribution: str | None = None,
) -> Result[NewsImage, str]:
    """Create an image for a news item."""
    match determine_image_type(stream, ALLOWED_IMAGE_TYPES):
        case Ok(image_type):
            pass
        case Err(e):
            return Err(e)

    if image_type != ImageType.svg:
        image_dimensions = determine_dimensions(stream)
        _check_image_dimensions(image_dimensions)

    image_id = NewsImageID(generate_uuid7())
    created_at = datetime.utcnow()
    number = _get_next_available_number(item.id)
    filename = f'{image_id}.{image_type.name}'

    db_image = DbNewsImage(
        image_id,
        created_at,
        creator.id,
        item.id,
        number,
        filename,
        alt_text=alt_text,
        caption=caption,
        attribution=attribution,
    )

    db.session.add(db_image)
    db.session.commit()

    image = _db_entity_to_image(db_image, item.channel.id)

    path = _assemble_image_file_path(item.channel.id, image.filename)

    # Might raise `FileExistsError`.
    upload.store(stream, path, create_parent_path_if_nonexistent=True)

    return Ok(image)


def _check_image_dimensions(image_dimensions: Dimensions) -> None:
    """Raise exception if image dimensions exceed defined maximum."""
    too_large = image_dimensions > MAXIMUM_DIMENSIONS
    if too_large:
        raise ValueError(
            'Image dimensions must not exceed '
            f'{MAXIMUM_DIMENSIONS.width} x {MAXIMUM_DIMENSIONS.height} pixels.'
        )


def _find_highest_number(item_id: NewsItemID) -> int | None:
    """Return the highest image number for that item, or `None` if the
    item has no images.
    """
    return db.session.scalar(
        select(db.func.max(DbNewsImage.number)).filter_by(item_id=item_id)
    )


def _get_next_available_number(item_id: NewsItemID) -> int:
    """Return the next available image number for that item."""
    highest_number = _find_highest_number(item_id)

    if highest_number is None:
        highest_number = 0

    return highest_number + 1


def update_image(
    image_id: NewsImageID,
    *,
    alt_text: str | None = None,
    caption: str | None = None,
    attribution: str | None = None,
) -> NewsImage:
    """Update a news image."""
    db_image = _get_db_image(image_id)

    db_image.alt_text = alt_text
    db_image.caption = caption
    db_image.attribution = attribution

    db.session.commit()

    return _db_entity_to_image(db_image, db_image.item.channel_id)


def delete_image(image_id: NewsImageID) -> None:
    """Delete a news image."""
    db_image = _get_db_image(image_id)

    # Delete file.
    channel_id = db_image.item.channel_id
    path = _assemble_image_file_path(channel_id, db_image.filename)
    upload.delete(path)

    # Delete database record.
    db.session.delete(db_image)
    db.session.commit()


def find_image(image_id: NewsImageID) -> NewsImage | None:
    """Return the image with that ID, or `None` if not found."""
    db_image = _find_db_image(image_id)

    if db_image is None:
        return None

    return _db_entity_to_image(db_image, db_image.item.channel_id)


def _find_db_image(image_id: NewsImageID) -> DbNewsImage | None:
    """Return the image with that ID, or `None` if not found."""
    return db.session.scalars(
        select(DbNewsImage)
        .filter(DbNewsImage.id == image_id)
        .options(
            db.joinedload(DbNewsImage.item).load_only(DbNewsItem.channel_id)
        )
    ).one_or_none()


def _get_db_image(image_id: NewsImageID) -> DbNewsImage:
    """Return the image with that ID."""
    db_image = _find_db_image(image_id)

    if db_image is None:
        raise ValueError(f'Unknown news image ID "{image_id}".')

    return db_image


def _assemble_image_file_path(channel_id: NewsChannelID, filename: str) -> Path:
    return (
        get_current_byceps_app().byceps_config.data_path
        / 'global'
        / 'news_channels'
        / channel_id
        / filename
    )


def _db_entity_to_image(
    db_image: DbNewsImage, channel_id: NewsChannelID
) -> NewsImage:
    url_path = f'/data/global/news_channels/{channel_id}/{db_image.filename}'

    return NewsImage(
        id=db_image.id,
        created_at=db_image.created_at,
        creator_id=db_image.creator_id,
        item_id=db_image.item_id,
        number=db_image.number,
        filename=db_image.filename,
        url_path=url_path,
        alt_text=db_image.alt_text,
        caption=db_image.caption,
        attribution=db_image.attribution,
    )
