# -*- coding: utf-8 -*-

"""
byceps.blueprints.user_avatar.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from flask import abort

from ...database import db
from ...util.image import create_thumbnail, Dimensions, guess_type, ImageType, \
    read_dimensions
from ...util import upload

from .models import Avatar


ALL_IMAGE_TYPES = frozenset(ImageType)

MAXIMUM_DIMENSIONS = Dimensions(110, 110)


def get_image_type_names(types):
    """Return the names of the image types."""
    return frozenset(t.name.upper() for t in types)


def update_avatar_image(user, stream):
    """Set a new avatar image for the user."""
    image_type = _determine_image_type(stream)

    if _is_image_too_large(stream):
        stream = create_thumbnail(stream, image_type.name, MAXIMUM_DIMENSIONS)

    avatar = Avatar(user, image_type)
    db.session.add(avatar)
    db.session.commit()

    # Might raise `FileExistsError`.
    upload.store(stream, avatar.path)

    user.avatar = avatar
    db.session.commit()


def _determine_image_type(stream):
    image_type = guess_type(stream)
    if image_type is None:
        abort(400, 'Only GIF, JPEG and PNG images are allowed.')

    stream.seek(0)
    return image_type


def _is_image_too_large(stream):
    actual_dimensions = read_dimensions(stream)
    stream.seek(0)
    return actual_dimensions > MAXIMUM_DIMENSIONS


def remove_avatar_image(user):
    """Remove the user's avatar image.

    The avatar will be unlinked from the user, but the database record
    as well as the image file itself won't be removed, though.
    """
    db.session.delete(user.avatar_selection)
    db.session.commit()
