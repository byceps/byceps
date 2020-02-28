"""
byceps.services.news.image_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import Optional

from ...database import db
from ...typing import UserID

from .models.image import Image as DbImage
from . import service as item_service
from .transfer.models import Image, ImageID, ItemID


def create_image(
    creator_id: UserID,
    item_id: ItemID,
    filename: str,
    *,
    alt_text: Optional[str] = None,
    caption: Optional[str] = None,
    attribution: Optional[str] = None,
) -> Image:
    """Create an image for a news item."""
    item = item_service.find_item(item_id)

    if item is None:
        raise ValueError(f'Unknown news item ID "{item_id}".')

    number = _get_next_available_number(item.id)

    image = DbImage(
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

    return _db_entity_to_image(image)


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
    filename: str,
    *,
    alt_text: Optional[str] = None,
    caption: Optional[str] = None,
    attribution: Optional[str] = None,
) -> None:
    """Update a news image."""
    image = _find_db_image(image_id)

    if image is None:
        raise ValueError(f'Unknown news image ID "{image_id}".')

    image.filename = filename
    image.alt_text = alt_text
    image.caption = caption
    image.attribution = attribution

    db.session.commit()


def find_image(image_id: ImageID) -> Optional[Image]:
    """Return the image with that id, or `None` if not found."""
    image = _find_db_image(image_id)

    if image is None:
        return None

    return _db_entity_to_image(image)


def _find_db_image(image_id: ImageID) -> Optional[DbImage]:
    """Return the image with that id, or `None` if not found."""
    return DbImage.query.get(image_id)


def _db_entity_to_image(image: DbImage) -> Image:
    return Image(
        id=image.id,
        created_at=image.created_at,
        creator_id=image.creator_id,
        item_id=image.item_id,
        number=image.number,
        filename=image.filename,
        alt_text=image.alt_text,
        caption=image.caption,
        attribution=image.attribution,
    )
