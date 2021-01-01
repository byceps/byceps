"""
byceps.services.user_group.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import List

from ...database import db
from ...typing import UserID

from .models import UserGroup


def create_group(creator_id: UserID, title: str, description: str) -> UserGroup:
    """Introduce a new group."""
    group = UserGroup(creator_id, title, description)

    db.session.add(group)
    db.session.commit()

    return group


def get_all_groups() -> List[UserGroup]:
    """Return all groups."""
    return UserGroup.query.all()
