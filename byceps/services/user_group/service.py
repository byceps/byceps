# -*- coding: utf-8 -*-

"""
byceps.services.user_group.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ...database import db

from .models import UserGroup


def create_group(creator_id, title, description):
    """Introduce a new badge."""
    group = UserGroup(creator_id, title, description)

    db.session.add(group)
    db.session.commit()

    return group


def get_all_groups():
    """Return all groups."""
    return UserGroup.query.all()
