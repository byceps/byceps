"""
byceps.services.user_group.user_group_repository
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import select

from byceps.database import db
from byceps.services.party.models import PartyID

from .dbmodels import DbUserGroup
from .models import UserGroup


def create_group(group: UserGroup) -> None:
    """Create a group."""
    db_group = DbUserGroup(
        group.id,
        group.party_id,
        group.created_at,
        group.creator.id,
        group.title,
        group.description,
    )

    db.session.add(db_group)
    db.session.commit()


def update_group(group: UserGroup) -> None:
    """Update a group."""
    db_group = find_group(group.id)
    if db_group is None:
        raise ValueError(f'Unknown user group ID "{group.id}"')

    db_group.title = group.title
    db_group.description = group.description

    db.session.commit()


def is_title_available(party_id: PartyID, title: str) -> bool:
    """Check if the title is yet unused."""
    return not db.session.scalar(
        select(
            db.exists()
            .where(DbUserGroup.party_id == party_id)
            .where(db.func.lower(DbUserGroup.title) == title.lower())
        )
    )


def find_group(group_id: UUID) -> DbUserGroup | None:
    """Return the group, if found."""
    return db.session.get(DbUserGroup, group_id)


def get_groups_for_party(party_id: PartyID) -> Sequence[DbUserGroup]:
    """Return user groups for a party."""
    return db.session.scalars(select(DbUserGroup)).all()
