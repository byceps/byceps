"""
byceps.services.user_group.user_group_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import select

from byceps.database import db
from byceps.services.user.models.user import User
from byceps.typing import PartyID

from .dbmodels import DbUserGroup


def create_group(
    party_id: PartyID,
    creator: User,
    title: str,
    description: str | None,
) -> DbUserGroup:
    """Introduce a new group."""
    group = DbUserGroup(party_id, creator.id, title, description)

    db.session.add(group)
    db.session.commit()

    return group


def get_all_groups() -> Sequence[DbUserGroup]:
    """Return all groups."""
    return db.session.scalars(select(DbUserGroup)).all()
