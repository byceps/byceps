"""
byceps.services.user_group.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from typing import Optional

from ...database import db
from ...typing import PartyID, UserID

from .dbmodels import UserGroup


def create_group(
    party_id: PartyID,
    creator_id: UserID,
    title: str,
    description: Optional[str],
) -> UserGroup:
    """Introduce a new group."""
    group = UserGroup(party_id, creator_id, title, description)

    db.session.add(group)
    db.session.commit()

    return group


def get_all_groups() -> list[UserGroup]:
    """Return all groups."""
    return UserGroup.query.all()
