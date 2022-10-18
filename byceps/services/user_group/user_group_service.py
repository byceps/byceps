"""
byceps.services.user_group.user_group_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Optional

from sqlalchemy import select

from ...database import db
from ...typing import PartyID, UserID

from .dbmodels import DbUserGroup


def create_group(
    party_id: PartyID,
    creator_id: UserID,
    title: str,
    description: Optional[str],
) -> DbUserGroup:
    """Introduce a new group."""
    group = DbUserGroup(party_id, creator_id, title, description)

    db.session.add(group)
    db.session.commit()

    return group


def get_all_groups() -> list[DbUserGroup]:
    """Return all groups."""
    return db.session.scalars(select(DbUserGroup)).all()
