"""
byceps.services.user.user_avatar_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from typing import BinaryIO

from sqlalchemy import select

from byceps.database import db
from byceps.services.image import image_service
from byceps.services.image.image_service import (
    ImageTypeProhibited,  # noqa: F401
)  # Provide to view functions.
from byceps.typing import UserID
from byceps.util import upload
from byceps.util.image import create_thumbnail
from byceps.util.image.models import Dimensions, ImageType

from . import user_log_service, user_service
from .dbmodels.avatar import DbUserAvatar
from .dbmodels.user import DbUser
from .models.user import UserAvatarID


MAXIMUM_DIMENSIONS = Dimensions(512, 512)


def update_avatar_image(
    user_id: UserID,
    stream: BinaryIO,
    allowed_types: set[ImageType],
    initiator_id: UserID,
    *,
    maximum_dimensions: Dimensions = MAXIMUM_DIMENSIONS,
) -> UserAvatarID:
    """Set a new avatar image for the user.

    Raise `ImageTypeProhibited` if the stream data is not of one the
    allowed types.
    """
    user = user_service.get_db_user(user_id)

    image_type = image_service.determine_image_type(stream, allowed_types)
    image_dimensions = image_service.determine_dimensions(stream)

    image_too_large = image_dimensions > maximum_dimensions
    if image_too_large or not image_dimensions.is_square:
        stream = create_thumbnail(
            stream, image_type.name, maximum_dimensions, force_square=True
        )

    avatar = DbUserAvatar(image_type)
    db.session.add(avatar)
    db.session.commit()

    # Might raise `FileExistsError`.
    upload.store(stream, avatar.path, create_parent_path_if_nonexistent=True)

    user.avatar_id = avatar.id

    log_entry = user_log_service.build_entry(
        'user-avatar-updated',
        user.id,
        {
            'avatar_id': str(avatar.id),
            'filename': str(avatar.filename),
            'initiator_id': str(initiator_id),
        },
    )
    db.session.add(log_entry)

    db.session.commit()

    return avatar.id


def remove_avatar_image(user_id: UserID, initiator_id: UserID) -> None:
    """Remove the user's avatar image.

    The avatar will be unlinked from the user, but the database record
    as well as the image file itself won't be removed, though.
    """
    user = user_service.get_db_user(user_id)

    if user.avatar_id is None:
        return

    log_entry = user_log_service.build_entry(
        'user-avatar-removed',
        user.id,
        {
            'avatar_id': str(user.avatar_id),
            'filename': str(user.avatar.filename),
            'initiator_id': str(initiator_id),
        },
    )
    db.session.add(log_entry)

    # Remove avatar reference *after* collecting values for log entry.
    user.avatar_id = None

    db.session.commit()


def get_db_avatar(avatar_id: UserAvatarID) -> DbUserAvatar:
    """Return the avatar with that ID, or raise exception if not found."""
    return db.session.execute(
        select(DbUserAvatar).filter_by(id=avatar_id)
    ).scalar_one()


def get_avatar_url_for_user(user_id: UserID) -> str | None:
    """Return the URL of the user's current avatar, or `None` if not set."""
    avatar_urls_by_user_id = get_avatar_urls_for_users({user_id})
    return avatar_urls_by_user_id.get(user_id)


def get_avatar_urls_for_users(
    user_ids: set[UserID],
) -> dict[UserID, str | None]:
    """Return the URLs of those users' current avatars."""
    if not user_ids:
        return {}

    user_ids_and_avatars = db.session.execute(
        select(
            DbUser.id,
            DbUserAvatar,
        )
        .join(DbUserAvatar, DbUser.avatar_id == DbUserAvatar.id)
        .filter(DbUser.id.in_(user_ids))
    ).all()

    urls_by_user_id = {
        user_id: avatar.url for user_id, avatar in user_ids_and_avatars
    }

    # Include all user IDs in result.
    return {user_id: urls_by_user_id.get(user_id) for user_id in user_ids}


def get_avatar_url_for_md5_email_address_hash(md5_hash: str) -> str | None:
    """Return the URL of the current avatar of the user with that hashed
    email address, or `None` if not set.
    """
    avatar = db.session.execute(
        select(DbUserAvatar)
        .join(DbUser)
        .filter(db.func.md5(DbUser.email_address) == md5_hash)
    ).scalar_one_or_none()

    if avatar is None:
        return None

    return avatar.url
