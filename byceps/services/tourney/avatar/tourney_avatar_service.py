"""
byceps.services.tourney.avatar.tourney_avatars_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime
from typing import BinaryIO
from uuid import UUID

from byceps.database import db
from byceps.services.party.models import PartyID
from byceps.services.user.models import User
from byceps.util import upload
from byceps.util.image.dimensions import determine_dimensions, Dimensions
from byceps.util.image.image_type import determine_image_type, ImageType
from byceps.util.image.thumbnail import create_thumbnail
from byceps.util.result import Err, Ok, Result
from byceps.util.uuid import generate_uuid7

from .dbmodels import DbTourneyAvatar
from .models import AvatarID


MAXIMUM_DIMENSIONS = Dimensions(512, 512)


def create_avatar_image(
    party_id: PartyID,
    creator: User,
    stream: BinaryIO,
    allowed_types: set[ImageType],
    *,
    maximum_dimensions: Dimensions = MAXIMUM_DIMENSIONS,
) -> Result[DbTourneyAvatar, str]:
    """Create a new avatar image."""
    avatar_id = AvatarID(generate_uuid7())
    created_at = datetime.utcnow()

    image_type_result = determine_image_type(stream, allowed_types)
    if image_type_result.is_err():
        return Err(image_type_result.unwrap_err())

    image_type = image_type_result.unwrap()
    image_dimensions = determine_dimensions(stream)

    image_too_large = image_dimensions > maximum_dimensions
    if image_too_large or not image_dimensions.is_square:
        stream = create_thumbnail(
            stream, image_type.name, maximum_dimensions, force_square=True
        )

    avatar = DbTourneyAvatar(
        avatar_id, party_id, created_at, creator.id, image_type
    )
    db.session.add(avatar)
    db.session.commit()

    # Might raise `FileExistsError`.
    upload.store(stream, avatar.path, create_parent_path_if_nonexistent=True)

    return Ok(avatar)


def delete_avatar_image(avatar_id: UUID) -> Result[None, str]:
    """Delete the avatar image."""
    avatar = db.session.get(DbTourneyAvatar, avatar_id)

    if avatar is None:
        return Err('Unknown avatar ID')

    # Delete file.
    upload.delete(avatar.path)

    # Delete database record.
    db.session.delete(avatar)
    db.session.commit()

    return Ok(None)
