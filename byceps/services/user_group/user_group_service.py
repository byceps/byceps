"""
byceps.services.user_group.user_group_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime
from uuid import UUID

from sqlalchemy import select

from byceps.database import db
from byceps.services.party.models import Party, PartyID
from byceps.services.user import user_service
from byceps.services.user.models.user import User, UserID

from . import user_group_domain_service
from .dbmodels import DbUserGroup
from .models import UserGroup


def create_group(
    party: Party,
    creator: User,
    title: str,
    description: str | None,
) -> UserGroup:
    """Create a group."""
    created_at = datetime.utcnow()

    group = user_group_domain_service.create_group(
        party, created_at, creator, title, description=description
    )

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

    return group


def update_group(group: UserGroup, title: str, description: str) -> None:
    """Update a group."""
    db_group = _get_db_group(group.id)
    if db_group is None:
        raise ValueError(f'Unknown user group ID "{group.id}"')

    db_group.title = title
    db_group.description = description or None

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


def find_group(group_id: UUID) -> UserGroup | None:
    """Return the group, if found."""
    db_group = _get_db_group(group_id)

    if db_group is None:
        return None

    creator = user_service.get_user(db_group.creator_id, include_avatar=True)
    return _db_entity_to_group(db_group, {creator.id: creator})


def _get_db_group(group_id: UUID) -> DbUserGroup | None:
    """Return the group, if found."""
    return db.session.get(DbUserGroup, group_id)


def get_groups_for_party(party_id: PartyID) -> list[UserGroup]:
    """Return user groups for a party."""
    db_groups = db.session.scalars(select(DbUserGroup)).all()

    user_ids = {db_group.creator_id for db_group in db_groups}
    users_by_id = user_service.get_users_indexed_by_id(
        user_ids, include_avatars=True
    )

    return [
        _db_entity_to_group(db_group, users_by_id) for db_group in db_groups
    ]


def _db_entity_to_group(
    db_group: DbUserGroup, users_by_id: dict[UserID, User]
) -> UserGroup:
    creator = users_by_id[db_group.creator_id]

    return UserGroup(
        id=db_group.id,
        party_id=db_group.party_id,
        created_at=db_group.created_at,
        creator=creator,
        title=db_group.title,
        description=db_group.description,
    )
