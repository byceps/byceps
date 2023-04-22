"""
byceps.services.news.news_image_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from typing import BinaryIO

from flask import current_app
from sqlalchemy import select

from byceps.database import db, generate_uuid7
from byceps.services.image import image_service
from byceps.services.image.image_service import ImageTypeProhibited
from byceps.services.user import user_service
from byceps.typing import UserID
from byceps.util import upload
from byceps.util.image.models import Dimensions, ImageType
from byceps.util.result import Err, Ok, Result

from . import news_item_service
from .dbmodels.image import DbNewsImage
from .dbmodels.item import DbNewsItem
from .models import NewsChannelID, NewsImage, NewsImageID, NewsItemID


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
    creator_id: UserID,
    item_id: NewsItemID,
    stream: BinaryIO,
    *,
    alt_text: str | None = None,
    caption: str | None = None,
    attribution: str | None = None,
) -> Result[NewsImage, str]:
    """Create an image for a news item."""
    creator = user_service.find_active_user(creator_id)
    if creator is None:
        raise user_service.UserIdRejected(creator_id)

    item = news_item_service.find_item(item_id)
    if item is None:
        raise ValueError(f'Unknown news item ID "{item_id}".')

    try:
        image_type = image_service.determine_image_type(
            stream, ALLOWED_IMAGE_TYPES
        )
    except ImageTypeProhibited as e:
        return Err(str(e))

    if image_type != ImageType.svg:
        image_dimensions = image_service.determine_dimensions(stream)
        _check_image_dimensions(image_dimensions)

    image_id = NewsImageID(generate_uuid7())
    number = _get_next_available_number(item.id)
    filename = f'{image_id}.{image_type.name}'

    db_image = DbNewsImage(
        image_id,
        creator_id,
        item.id,
        number,
        filename,
        alt_text=alt_text,
        caption=caption,
        attribution=attribution,
    )

    db.session.add(db_image)
    db.session.commit()

    path = (
        current_app.config['PATH_DATA']
        / 'global'
        / 'news_channels'
        / item.channel.id
        / filename
    )

    # Might raise `FileExistsError`.
    upload.store(stream, path, create_parent_path_if_nonexistent=True)

    image = _db_entity_to_image(db_image, item.channel.id)

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
    db_image = _find_db_image(image_id)

    if db_image is None:
        raise ValueError(f'Unknown news image ID "{image_id}".')

    db_image.alt_text = alt_text
    db_image.caption = caption
    db_image.attribution = attribution

    db.session.commit()

    return _db_entity_to_image(db_image, db_image.item.channel_id)


def find_image(image_id: NewsImageID) -> NewsImage | None:
    """Return the image with that id, or `None` if not found."""
    db_image = _find_db_image(image_id)

    if db_image is None:
        return None

    return _db_entity_to_image(db_image, db_image.item.channel_id)


def _find_db_image(image_id: NewsImageID) -> DbNewsImage | None:
    """Return the image with that id, or `None` if not found."""
    return db.session.scalars(
        select(DbNewsImage)
        .filter(DbNewsImage.id == image_id)
        .options(
            db.joinedload(DbNewsImage.item).load_only(DbNewsItem.channel_id)
        )
    ).one_or_none()


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
