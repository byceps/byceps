"""
byceps.services.user.user_avatar_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import BinaryIO

from flask import current_app

from byceps.database import db
from byceps.events.user import (
    UserAvatarRemovedEvent,
    UserAvatarUpdatedEvent,
)
from byceps.util import upload
from byceps.util.image.dimensions import determine_dimensions, Dimensions
from byceps.util.image.image_type import determine_image_type, ImageType
from byceps.util.image.thumbnail import create_thumbnail
from byceps.util.result import Err, Ok, Result

from . import user_avatar_domain_service, user_log_service, user_service
from .dbmodels.avatar import DbUserAvatar
from .models.user import User, UserAvatar


MAXIMUM_DIMENSIONS = Dimensions(512, 512)


def update_avatar_image(
    user: User,
    stream: BinaryIO,
    allowed_types: set[ImageType],
    initiator: User,
    *,
    maximum_dimensions: Dimensions = MAXIMUM_DIMENSIONS,
) -> Result[tuple[UserAvatar, UserAvatarUpdatedEvent], str]:
    """Set a new avatar image for the user."""
    db_user = user_service.get_db_user(user.id)

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

    db_avatar = DbUserAvatar(image_type)
    db.session.add(db_avatar)
    db.session.commit()

    avatar = _db_entity_to_item(db_avatar)

    # Might raise `FileExistsError`.
    upload.store(stream, avatar.path, create_parent_path_if_nonexistent=True)

    db_user.avatar_id = avatar.id

    event, log_entry = user_avatar_domain_service.update_avatar_image(
        user, avatar, initiator
    )

    db_log_entry = user_log_service.to_db_entry(log_entry)
    db.session.add(db_log_entry)

    db.session.commit()

    return Ok((avatar, event))


def remove_avatar_image(
    user: User, initiator: User
) -> UserAvatarRemovedEvent | None:
    """Remove the user's avatar image.

    The avatar will be unlinked from the user, but the database record
    as well as the image file itself won't be removed, though.
    """
    db_user = user_service.get_db_user(user.id)

    if db_user.avatar_id is None:
        return None

    avatar = _db_entity_to_item(db_user.avatar)

    event, log_entry = user_avatar_domain_service.remove_avatar_image(
        user, avatar, initiator
    )

    db_log_entry = user_log_service.to_db_entry(log_entry)
    db.session.add(db_log_entry)

    # Remove avatar reference *after* collecting values for log entry.
    db_user.avatar_id = None

    db.session.commit()

    return event


def _db_entity_to_item(db_avatar: DbUserAvatar) -> UserAvatar:
    images_path = (
        current_app.config['PATH_DATA'] / 'global' / 'users' / 'avatars'
    )
    path = images_path / db_avatar.filename

    return UserAvatar(
        id=db_avatar.id,
        created_at=db_avatar.created_at,
        image_type=db_avatar.image_type,
        filename=db_avatar.filename,
        path=path,
        url=db_avatar.url,
    )
