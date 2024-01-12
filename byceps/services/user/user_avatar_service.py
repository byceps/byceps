"""
byceps.services.user.user_avatar_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2024 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import BinaryIO

from sqlalchemy import select

from byceps.database import db
from byceps.services.image import image_service
from byceps.util import upload
from byceps.util.image import create_thumbnail
from byceps.util.image.models import Dimensions, ImageType
from byceps.util.result import Err, Ok, Result

from . import user_log_service, user_service
from .dbmodels.avatar import DbUserAvatar
from .dbmodels.user import DbUser
from .models.user import User, UserAvatarID, UserID


MAXIMUM_DIMENSIONS = Dimensions(512, 512)


def update_avatar_image(
    user_id: UserID,
    stream: BinaryIO,
    allowed_types: set[ImageType],
    initiator: User,
    *,
    maximum_dimensions: Dimensions = MAXIMUM_DIMENSIONS,
) -> Result[UserAvatarID, str]:
    """Set a new avatar image for the user."""
    db_user = user_service.get_db_user(user_id)

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

    db_avatar = DbUserAvatar(image_type)
    db.session.add(db_avatar)
    db.session.commit()

    # Might raise `FileExistsError`.
    upload.store(stream, db_avatar.path, create_parent_path_if_nonexistent=True)

    db_user.avatar_id = db_avatar.id

    db_log_entry = user_log_service.build_entry(
        'user-avatar-updated',
        db_user.id,
        {
            'avatar_id': str(db_avatar.id),
            'filename': str(db_avatar.filename),
            'initiator_id': str(initiator.id),
        },
    )
    db.session.add(db_log_entry)

    db.session.commit()

    return Ok(db_avatar.id)


def remove_avatar_image(user_id: UserID, initiator: User) -> None:
    """Remove the user's avatar image.

    The avatar will be unlinked from the user, but the database record
    as well as the image file itself won't be removed, though.
    """
    db_user = user_service.get_db_user(user_id)

    if db_user.avatar_id is None:
        return

    db_log_entry = user_log_service.build_entry(
        'user-avatar-removed',
        db_user.id,
        {
            'avatar_id': str(db_user.avatar_id),
            'filename': str(db_user.avatar.filename),
            'initiator_id': str(initiator.id),
        },
    )
    db.session.add(db_log_entry)

    # Remove avatar reference *after* collecting values for log entry.
    db_user.avatar_id = None

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

    user_ids_and_db_avatars = db.session.execute(
        select(
            DbUser.id,
            DbUserAvatar,
        )
        .join(DbUserAvatar, DbUser.avatar_id == DbUserAvatar.id)
        .filter(DbUser.id.in_(user_ids))
    ).all()

    urls_by_user_id = {
        user_id: db_avatar.url for user_id, db_avatar in user_ids_and_db_avatars
    }

    # Include all user IDs in result.
    return {user_id: urls_by_user_id.get(user_id) for user_id in user_ids}


def get_avatar_url_for_md5_email_address_hash(md5_hash: str) -> str | None:
    """Return the URL of the current avatar of the user with that hashed
    email address, or `None` if not set.
    """
    db_avatar = db.session.execute(
        select(DbUserAvatar)
        .join(DbUser)
        .filter(db.func.md5(DbUser.email_address) == md5_hash)
    ).scalar_one_or_none()

    if db_avatar is None:
        return None

    return db_avatar.url
