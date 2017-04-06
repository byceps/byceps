"""
byceps.services.user_avatar.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ...database import db
from ...util.image import create_thumbnail
from ...util.image.models import Dimensions
from ...util import upload

from ..image import service as image_service
from ..image.service import ImageTypeProhibited

from .models import Avatar, AvatarCreationTuple, AvatarSelection


MAXIMUM_DIMENSIONS = Dimensions(512, 512)


def update_avatar_image(user, stream, *, allowed_types=None,
                        maximum_dimensions=MAXIMUM_DIMENSIONS):
    """Set a new avatar image for the user."""
    if allowed_types is None:
        allowed_types = image_service.get_all_image_types()

    image_type = image_service.determine_image_type(stream, allowed_types)
    image_dimensions = image_service.determine_dimensions(stream)

    image_too_large = image_dimensions > maximum_dimensions
    if image_too_large or not image_dimensions.is_square:
        stream = create_thumbnail(stream, image_type.name, maximum_dimensions)

    avatar = Avatar(user.id, image_type)
    db.session.add(avatar)
    db.session.commit()

    # Might raise `FileExistsError`.
    upload.store(stream, avatar.path)

    user.avatar = avatar
    db.session.commit()


def remove_avatar_image(user):
    """Remove the user's avatar image.

    The avatar will be unlinked from the user, but the database record
    as well as the image file itself won't be removed, though.
    """
    db.session.delete(user.avatar_selection)
    db.session.commit()


def get_avatars_uploaded_by_user(user_id):
    """Return the avatars uploaded by the user."""
    avatars = Avatar.query \
        .filter_by(creator_id=user_id) \
        .all()

    return [AvatarCreationTuple(avatar.created_at, avatar.url)
            for avatar in avatars]


def get_avatar_url_for_user(user_id):
    """Return the URL of the user's current avatar, or `None` if not set."""
    avatar_urls_by_user_id = get_avatar_urls_for_users({user_id})
    return avatar_urls_by_user_id.get(user_id)


def get_avatar_urls_for_users(user_ids):
    """Return the URLs of those users' current avatars."""
    if not user_ids:
        return {}

    user_ids_and_avatars = db.session.query(AvatarSelection.user_id, Avatar) \
        .join(Avatar) \
        .filter(AvatarSelection.user_id.in_(user_ids)) \
        .all()

    urls_by_user_id = {user_id: avatar.url
                       for user_id, avatar in user_ids_and_avatars}

    # Include all user IDs in result.
    return {user_id: urls_by_user_id.get(user_id) for user_id in user_ids}
