"""
byceps.services.news.image_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import Optional

from ...database import db
from ...typing import UserID

from .models.image import Image as DbImage
from .transfer.models import Image, ItemID


def create_image(
    creator_id: UserID,
    item_id: ItemID,
    filename: str,
    *,
    alt_text: Optional[str] = None,
    caption: Optional[str] = None,
) -> Image:
    """Create an image for a news item."""
    image = DbImage(creator_id, item_id, filename, alt_text=alt_text,
                    caption=caption)

    db.session.add(image)
    db.session.commit()

    return _db_entity_to_image(image)


def _db_entity_to_image(image: DbImage) -> Image:
    return Image(
        id=image.id,
        created_at=image.created_at,
        creator_id=image.creator_id,
        item_id=image.item_id,
        filename=image.filename,
        alt_text=image.alt_text,
        caption=image.caption,
    )
