"""
byceps.services.news.news_image_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import BinaryIO, Optional

from flask import current_app

from ...database import db, generate_uuid
from ...typing import UserID
from ...util import upload
from ...util.image.models import Dimensions, ImageType

from ..image import image_service
from ..user import user_service

from .dbmodels.image import DbImage
from . import news_item_service
from .transfer.models import ChannelID, Image, ImageID, ItemID


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
    item_id: ItemID,
    stream: BinaryIO,
    *,
    alt_text: Optional[str] = None,
    caption: Optional[str] = None,
    attribution: Optional[str] = None,
) -> Image:
    """Create an image for a news item."""
    creator = user_service.find_active_user(creator_id)
    if creator is None:
        raise user_service.UserIdRejected(creator_id)

    item = news_item_service.find_item(item_id)
    if item is None:
        raise ValueError(f'Unknown news item ID "{item_id}".')

    # Might raise `ImageTypeProhibited`.
    image_type = image_service.determine_image_type(stream, ALLOWED_IMAGE_TYPES)

    if image_type != ImageType.svg:
        image_dimensions = image_service.determine_dimensions(stream)
        _check_image_dimensions(image_dimensions)

    image_id = ImageID(generate_uuid())
    number = _get_next_available_number(item.id)
    filename = f'{image_id}.{image_type.name}'

    db_image = DbImage(
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

    return _db_entity_to_image(db_image, item.channel.id)


def _check_image_dimensions(image_dimensions: Dimensions) -> None:
    """Raise exception if image dimensions exceed defined maximum."""
    too_large = image_dimensions > MAXIMUM_DIMENSIONS
    if too_large:
        raise ValueError(
            'Image dimensions must not exceed '
            f'{MAXIMUM_DIMENSIONS.width} x {MAXIMUM_DIMENSIONS.height} pixels.'
        )


def _find_highest_number(item_id: ItemID) -> Optional[int]:
    """Return the highest image number for that item, or `None` if the
    item has no images.
    """
    return db.session \
        .query(db.func.max(DbImage.number)) \
        .filter_by(item_id=item_id) \
        .scalar()


def _get_next_available_number(item_id: ItemID) -> int:
    """Return the next available image number for that item."""
    highest_number = _find_highest_number(item_id)

    if highest_number is None:
        highest_number = 0

    return highest_number + 1


def update_image(
    image_id: ImageID,
    *,
    alt_text: Optional[str] = None,
    caption: Optional[str] = None,
    attribution: Optional[str] = None,
) -> Image:
    """Update a news image."""
    db_image = _find_db_image(image_id)

    if db_image is None:
        raise ValueError(f'Unknown news image ID "{image_id}".')

    db_image.alt_text = alt_text
    db_image.caption = caption
    db_image.attribution = attribution

    db.session.commit()

    return _db_entity_to_image(db_image, db_image.item.channel_id)


def find_image(image_id: ImageID) -> Optional[Image]:
    """Return the image with that id, or `None` if not found."""
    db_image = _find_db_image(image_id)

    if db_image is None:
        return None

    return _db_entity_to_image(db_image, db_image.item.channel_id)


def _find_db_image(image_id: ImageID) -> Optional[DbImage]:
    """Return the image with that id, or `None` if not found."""
    return db.session \
        .query(DbImage) \
        .options(db.joinedload(DbImage.item).load_only('channel_id')) \
        .get(image_id)


def _db_entity_to_image(db_image: DbImage, channel_id: ChannelID) -> Image:
    url_path = f'/data/global/news_channels/{channel_id}/{db_image.filename}'

    return Image(
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
