"""
byceps.services.user.user_avatar_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2024 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime, UTC
from typing import BinaryIO

from sqlalchemy import select

from byceps.database import db
from byceps.services.image import image_service
from byceps.util import upload
from byceps.util.image import create_thumbnail
from byceps.util.image.models import Dimensions, ImageType
from byceps.util.result import Err, Ok, Result
from byceps.util.uuid import generate_uuid7

from . import user_log_service, user_service
from .dbmodels.avatar import DbUserAvatar
from .dbmodels.user import DbUser
from .models.log import UserLogEntry
from .models.user import User, UserAvatar, UserID


MAXIMUM_DIMENSIONS = Dimensions(512, 512)


def update_avatar_image(
    user: User,
    stream: BinaryIO,
    allowed_types: set[ImageType],
    initiator: User,
    *,
    maximum_dimensions: Dimensions = MAXIMUM_DIMENSIONS,
) -> Result[UserAvatar, str]:
    """Set a new avatar image for the user."""
    db_user = user_service.get_db_user(user.id)

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

    avatar = _db_entity_to_item(db_avatar)

    occurred_at = datetime.now(UTC)

    # Might raise `FileExistsError`.
    upload.store(stream, avatar.path, create_parent_path_if_nonexistent=True)

    db_user.avatar_id = avatar.id

    log_entry = _build_avatar_updated_log_entry(
        occurred_at, user, initiator, avatar
    )

    db_log_entry = user_log_service.to_db_entry(log_entry)
    db.session.add(db_log_entry)

    db.session.commit()

    return Ok(avatar)


def _build_avatar_updated_log_entry(
    occurred_at: datetime,
    user: User,
    initiator: User,
    avatar: UserAvatar,
) -> UserLogEntry:
    return UserLogEntry(
        id=generate_uuid7(),
        occurred_at=occurred_at,
        event_type='user-avatar-updated',
        user_id=user.id,
        initiator_id=initiator.id,
        data={
            'avatar_id': str(avatar.id),
            'filename': str(avatar.filename),
        },
    )


def remove_avatar_image(user: User, initiator: User) -> None:
    """Remove the user's avatar image.

    The avatar will be unlinked from the user, but the database record
    as well as the image file itself won't be removed, though.
    """
    db_user = user_service.get_db_user(user.id)

    if db_user.avatar_id is None:
        return

    avatar = _db_entity_to_item(db_user.avatar)

    occurred_at = datetime.now(UTC)

    log_entry = _build_avatar_removed_log_entry(
        occurred_at, user, initiator, avatar
    )

    db_log_entry = user_log_service.to_db_entry(log_entry)
    db.session.add(db_log_entry)

    # Remove avatar reference *after* collecting values for log entry.
    db_user.avatar_id = None

    db.session.commit()


def _build_avatar_removed_log_entry(
    occurred_at: datetime,
    user: User,
    initiator: User,
    avatar: UserAvatar,
) -> UserLogEntry:
    return UserLogEntry(
        id=generate_uuid7(),
        occurred_at=occurred_at,
        event_type='user-avatar-removed',
        user_id=user.id,
        initiator_id=initiator.id,
        data={
            'avatar_id': str(avatar.id),
            'filename': str(avatar.filename),
        },
    )


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


def _db_entity_to_item(db_avatar: DbUserAvatar) -> UserAvatar:
    return UserAvatar(
        id=db_avatar.id,
        created_at=db_avatar.created_at,
        image_type=db_avatar.image_type,
        filename=db_avatar.filename,
        path=db_avatar.path,
        url=db_avatar.url,
    )
