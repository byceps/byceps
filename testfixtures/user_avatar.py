# -*- coding: utf-8 -*-

"""
testfixtures.user_avatar
~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime

from byceps.blueprints.user_avatar.models import Avatar
from byceps.database import generate_uuid
from byceps.util.image import ImageType


def create_avatar(creator, *, created_at=None, image_type=ImageType.jpeg):
    if created_at is None:
        created_at = datetime.utcnow()

    avatar = Avatar(creator, image_type)
    avatar.id = generate_uuid()
    avatar.created_at = created_at
    return avatar
