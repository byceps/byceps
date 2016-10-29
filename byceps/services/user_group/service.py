# -*- coding: utf-8 -*-

"""
byceps.services.user_group.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ...database import db

from .models import UserGroup


def create_group(creator, title, description):
    """Introduce a new badge."""
    group = UserGroup(creator, title, description)

    db.session.add(group)
    db.session.commit()

    return group


def get_all_groups():
    """Return all groups."""
    return UserGroup.query.all()
