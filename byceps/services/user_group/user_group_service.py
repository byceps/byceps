"""
byceps.services.user_group.user_group_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from uuid import UUID

from byceps.services.party.models import Party, PartyID
from byceps.services.user import user_service
from byceps.services.user.models import User, UserID

from . import user_group_domain_service, user_group_repository
from .dbmodels import DbUserGroup
from .events import (
    UserGroupCreatedEvent,
    UserGroupDeletedEvent,
    UserGroupMemberAddedEvent,
    UserGroupMemberRemovedEvent,
)
from .models import UserGroup, UserGroupMembership


# -------------------------------------------------------------------- #
# groups


def create_group(
    party: Party,
    creator: User,
    title: str,
    description: str | None,
) -> tuple[UserGroup, UserGroupCreatedEvent]:
    """Create a group."""
    group, event = user_group_domain_service.create_group(
        party, creator, title, description=description
    )

    user_group_repository.create_group(group)

    return group, event


def update_group(group: UserGroup, title: str, description: str | None) -> None:
    """Update a group."""
    updated_group = user_group_domain_service.update_group(
        group, title, description
    )

    user_group_repository.update_group(updated_group)


def delete_group(group: UserGroup, initiator: User) -> UserGroupDeletedEvent:
    """Delete a group."""
    event = user_group_domain_service.delete_group(group, initiator)

    user_group_repository.delete_group(group.id)

    return event


def is_title_available(party_id: PartyID, title: str) -> bool:
    """Check if the title is yet unused."""
    return user_group_repository.is_title_available(party_id, title)


def find_group(group_id: UUID) -> UserGroup | None:
    """Return the group, if found."""
    db_group = user_group_repository.find_group(group_id)

    if db_group is None:
        return None

    creator = user_service.get_user(db_group.creator_id, include_avatar=True)
    return _db_entity_to_group(db_group, {creator.id: creator})


def get_groups_for_party(party_id: PartyID) -> list[UserGroup]:
    """Return user groups for a party."""
    db_groups = user_group_repository.get_groups_for_party(party_id)

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


# -------------------------------------------------------------------- #
# memberships


def add_member(
    group: UserGroup, user: User, initiator: User
) -> tuple[UserGroupMembership, UserGroupMemberAddedEvent]:
    """Add a user to a group."""
    membership, event = user_group_domain_service.add_member(
        group, user, initiator
    )

    user_group_repository.create_membership(membership)

    return membership, event


def remove_member(
    group: UserGroup, membership: UserGroupMembership, initiator: User
) -> UserGroupMemberRemovedEvent:
    """Remove a member from a group."""
    event = user_group_domain_service.remove_member(
        group, membership, initiator
    )

    user_group_repository.delete_membership(membership.id)

    return event
