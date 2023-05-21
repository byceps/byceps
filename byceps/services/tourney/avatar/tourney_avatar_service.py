"""
byceps.services.tourney.avatar.tourney_avatars_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import BinaryIO
from uuid import UUID

from byceps.database import db
from byceps.services.image import image_service
from byceps.services.user import user_service
from byceps.typing import PartyID, UserID
from byceps.util import upload
from byceps.util.image import create_thumbnail
from byceps.util.image.models import Dimensions, ImageType
from byceps.util.result import Err, Ok, Result

from .dbmodels import DbTourneyAvatar


MAXIMUM_DIMENSIONS = Dimensions(512, 512)


def create_avatar_image(
    party_id: PartyID,
    creator_id: UserID,
    stream: BinaryIO,
    allowed_types: set[ImageType],
    *,
    maximum_dimensions: Dimensions = MAXIMUM_DIMENSIONS,
) -> Result[DbTourneyAvatar, str]:
    """Create a new avatar image."""
    creator = user_service.find_active_user(creator_id)
    if creator is None:
        raise user_service.UserIdRejectedError(creator_id)

    image_type_result = image_service.determine_image_type(
        stream, allowed_types
    )
    if image_type_result.is_err():
        return Err(image_type_result.unwrap_err())

    image_type = image_type_result.unwrap()
    image_dimensions = image_service.determine_dimensions(stream)

    image_too_large = image_dimensions > maximum_dimensions
    if image_too_large or not image_dimensions.is_square:
        stream = create_thumbnail(
            stream, image_type.name, maximum_dimensions, force_square=True
        )

    avatar = DbTourneyAvatar(party_id, creator_id, image_type)
    db.session.add(avatar)
    db.session.commit()

    # Might raise `FileExistsError`.
    upload.store(stream, avatar.path, create_parent_path_if_nonexistent=True)

    return Ok(avatar)


def delete_avatar_image(avatar_id: UUID) -> None:
    """Delete the avatar image."""
    avatar = db.session.get(DbTourneyAvatar, avatar_id)

    if avatar is None:
        raise ValueError('Unknown avatar ID')

    # Delete file.
    upload.delete(avatar.path)

    # Delete database record.
    db.session.delete(avatar)
    db.session.commit()
