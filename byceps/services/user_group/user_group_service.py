"""
byceps.services.user_group.user_group_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2024 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

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
