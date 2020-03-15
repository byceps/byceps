"""
byceps.services.user_avatar.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import BinaryIO, Dict, List, Optional, Set

from ...database import db
from ...typing import UserID
from ...util.image import create_thumbnail
from ...util.image.models import Dimensions, ImageType
from ...util import upload

from ..image import service as image_service
from ..image.service import ImageTypeProhibited  # Provide to view functions.
from ..user import service as user_service

from .models import Avatar as DbAvatar, AvatarSelection as DbAvatarSelection
from .transfer.models import AvatarUpdate


MAXIMUM_DIMENSIONS = Dimensions(512, 512)


def update_avatar_image(
    user_id: UserID,
    stream: BinaryIO,
    allowed_types: Set[ImageType],
    *,
    maximum_dimensions: Dimensions = MAXIMUM_DIMENSIONS,
) -> None:
    """Set a new avatar image for the user.

    Raise `ImageTypeProhibited` if the stream data is not of one the
    allowed types.
    """
    user = user_service.find_active_user(user_id)
    if user is None:
        raise user_service.UserIdRejected(user_id)

    image_type = image_service.determine_image_type(stream, allowed_types)
    image_dimensions = image_service.determine_dimensions(stream)

    image_too_large = image_dimensions > maximum_dimensions
    if image_too_large or not image_dimensions.is_square:
        stream = create_thumbnail(
            stream, image_type.name, maximum_dimensions, force_square=True
        )

    avatar = DbAvatar(user.id, image_type)
    db.session.add(avatar)
    db.session.commit()

    # Might raise `FileExistsError`.
    upload.store(stream, avatar.path)

    user.avatar = avatar
    db.session.commit()


def remove_avatar_image(user_id: UserID) -> None:
    """Remove the user's avatar image.

    The avatar will be unlinked from the user, but the database record
    as well as the image file itself won't be removed, though.
    """
    selection = DbAvatarSelection.query.get(user_id)

    if selection is None:
        raise ValueError(f'No avatar set for user ID {user_id}.')

    db.session.delete(selection)
    db.session.commit()


def get_avatars_uploaded_by_user(user_id: UserID) -> List[AvatarUpdate]:
    """Return the avatars uploaded by the user."""
    avatars = DbAvatar.query \
        .filter_by(creator_id=user_id) \
        .all()

    return [AvatarUpdate(avatar.created_at, avatar.url) for avatar in avatars]


def get_avatar_url_for_user(user_id: UserID) -> Optional[str]:
    """Return the URL of the user's current avatar, or `None` if not set."""
    avatar_urls_by_user_id = get_avatar_urls_for_users({user_id})
    return avatar_urls_by_user_id.get(user_id)


def get_avatar_urls_for_users(user_ids: Set[UserID]) -> Dict[UserID, str]:
    """Return the URLs of those users' current avatars."""
    if not user_ids:
        return {}

    user_ids_and_avatars = db.session.query(
            DbAvatarSelection.user_id,
            DbAvatar,
        ) \
        .join(DbAvatar) \
        .filter(DbAvatarSelection.user_id.in_(user_ids)) \
        .all()

    urls_by_user_id = {
        user_id: avatar.url for user_id, avatar in user_ids_and_avatars
    }

    # Include all user IDs in result.
    return {user_id: urls_by_user_id.get(user_id) for user_id in user_ids}
