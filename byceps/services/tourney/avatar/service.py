"""
byceps.services.tourney.avatar.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from uuid import UUID
from typing import BinaryIO, Set

from ....database import db
from ....typing import PartyID, UserID
from ....util.image import create_thumbnail
from ....util.image.models import Dimensions, ImageType
from ....util import upload

from ...image import service as image_service
from ...image.service import ImageTypeProhibited  # Provide to view functions.
from ...user import service as user_service

from .dbmodels import Avatar


MAXIMUM_DIMENSIONS = Dimensions(512, 512)


def create_avatar_image(
    party_id: PartyID,
    creator_id: UserID,
    stream: BinaryIO,
    allowed_types: Set[ImageType],
    *,
    maximum_dimensions: Dimensions = MAXIMUM_DIMENSIONS,
) -> Avatar:
    """Create a new avatar image.

    Raise `ImageTypeProhibited` if the stream data is not of one the
    allowed types.
    """
    creator = user_service.find_active_user(creator_id)
    if creator is None:
        raise user_service.UserIdRejected(creator_id)

    image_type = image_service.determine_image_type(stream, allowed_types)
    image_dimensions = image_service.determine_dimensions(stream)

    image_too_large = image_dimensions > maximum_dimensions
    if image_too_large or not image_dimensions.is_square:
        stream = create_thumbnail(
            stream, image_type.name, maximum_dimensions, force_square=True
        )

    avatar = Avatar(party_id, creator_id, image_type)
    db.session.add(avatar)
    db.session.commit()

    # Might raise `FileExistsError`.
    upload.store(stream, avatar.path, create_parent_path_if_nonexistent=True)

    return avatar


def delete_avatar_image(avatar_id: UUID) -> None:
    """Delete the avatar image."""
    avatar = Avatar.query.get(avatar_id)

    if avatar is None:
        raise ValueError('Unknown avatar ID')

    # Delete file.
    upload.delete(avatar.path)

    # Delete database record.
    db.session.delete(avatar)
    db.session.commit()
