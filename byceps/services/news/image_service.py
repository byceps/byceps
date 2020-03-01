"""
byceps.services.news.image_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import BinaryIO, Optional

from flask import current_app

from ...database import db, generate_uuid
from ...typing import UserID
from ...util import upload
from ...util.image.models import Dimensions, ImageType

from ..image import service as image_service
from ..user import service as user_service

from .models.image import Image as DbImage
from . import service as item_service
from .transfer.models import ChannelID, Image, ImageID, ItemID


ALLOWED_IMAGE_TYPES = frozenset([
    ImageType.jpeg,
    ImageType.png,
    ImageType.svg,
])


MAXIMUM_DIMENSIONS = Dimensions(1280, 1280)


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

    item = item_service.find_item(item_id)
    if item is None:
        raise ValueError(f'Unknown news item ID "{item_id}".')

    # Might raise `ImageTypeProhibited`.
    image_type = image_service.determine_image_type(stream, ALLOWED_IMAGE_TYPES)

    if image_type != ImageType.svg:
        image_dimensions = image_service.determine_dimensions(stream)
        _check_image_dimensions(image_dimensions)

    image_id = generate_uuid()
    number = _get_next_available_number(item.id)
    filename = f'{image_id}.{image_type.name}'

    image = DbImage(
        image_id,
        creator_id,
        item.id,
        number,
        filename,
        alt_text=alt_text,
        caption=caption,
        attribution=attribution,
    )

    db.session.add(image)
    db.session.commit()

    path = (
        current_app.config['PATH_DATA']
        / 'global'
        / 'news_channels'
        / item.channel.id
        / filename
    )

    # Might raise `FileExistsError`.
    upload.store(stream, path, create_parent_path_if_nonexistant=True)

    return _db_entity_to_image(image, item.channel.id)


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
) -> None:
    """Update a news image."""
    image = _find_db_image(image_id)

    if image is None:
        raise ValueError(f'Unknown news image ID "{image_id}".')

    image.alt_text = alt_text
    image.caption = caption
    image.attribution = attribution

    db.session.commit()


def find_image(image_id: ImageID) -> Optional[Image]:
    """Return the image with that id, or `None` if not found."""
    image = _find_db_image(image_id)

    if image is None:
        return None

    return _db_entity_to_image(image, image.item.channel_id)


def _find_db_image(image_id: ImageID) -> Optional[DbImage]:
    """Return the image with that id, or `None` if not found."""
    return DbImage.query \
        .options(db.joinedload('item').load_only('channel_id')) \
        .get(image_id)


def _db_entity_to_image(image: DbImage, channel_id: ChannelID) -> Image:
    url_path = f'/data/global/news_channels/{channel_id}/{image.filename}'

    return Image(
        id=image.id,
        created_at=image.created_at,
        creator_id=image.creator_id,
        item_id=image.item_id,
        number=image.number,
        filename=image.filename,
        url_path=url_path,
        alt_text=image.alt_text,
        caption=image.caption,
        attribution=image.attribution,
    )
