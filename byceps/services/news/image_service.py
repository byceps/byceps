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
    image = DbImage(
        creator_id,
        item_id,
        filename,
        alt_text=alt_text,
        caption=caption,
        attribution=attribution,
    )

    db.session.add(image)
    db.session.commit()

    return _db_entity_to_image(image)


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
        filename=image.filename,
        alt_text=image.alt_text,
        caption=image.caption,
        attribution=image.attribution,
    )
