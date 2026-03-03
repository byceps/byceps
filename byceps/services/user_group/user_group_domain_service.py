"""
byceps.services.user_group.user_group_domain_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import dataclasses
from datetime import datetime

from byceps.services.party.models import Party
from byceps.services.user.models import User
from byceps.util.uuid import generate_uuid7

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
    *,
    description: str | None = None,
) -> tuple[UserGroup, UserGroupCreatedEvent]:
    """Create a group."""
    group_id = generate_uuid7()
    created_at = datetime.utcnow()

    group = UserGroup(
        id=group_id,
        party_id=party.id,
        created_at=created_at,
        creator=creator,
        title=title,
        description=description,
    )

    event = _build_group_created_event(group, created_at, creator)

    return group, event


def _build_group_created_event(
    group: UserGroup, occurred_at: datetime, creator: User
) -> UserGroupCreatedEvent:
    return UserGroupCreatedEvent(
        occurred_at=occurred_at,
        initiator=creator,
        group=group,
    )


def update_group(
    group: UserGroup, title: str, description: str | None
) -> UserGroup:
    """Update a group."""
    return dataclasses.replace(
        group,
        title=title,
        description=description,
    )


def delete_group(group: UserGroup, initiator: User) -> UserGroupDeletedEvent:
    """Delete a group."""
    occurred_at = datetime.utcnow()

    event = _build_group_deleted_event(group, occurred_at, initiator)

    return event


def _build_group_deleted_event(
    group: UserGroup, occurred_at: datetime, initiator: User
) -> UserGroupDeletedEvent:
    return UserGroupDeletedEvent(
        occurred_at=occurred_at,
        initiator=initiator,
        group=group,
    )


# -------------------------------------------------------------------- #
# memberships


def add_member(
    group: UserGroup, user: User, initiator: User
) -> tuple[UserGroupMembership, UserGroupMemberAddedEvent]:
    """Add a user to a group."""
    membership_id = generate_uuid7()
    created_at = datetime.utcnow()

    membership = UserGroupMembership(
        id=membership_id,
        created_at=created_at,
        group_id=group.id,
        user=user,
    )

    event = _build_member_added_event(group, user, created_at, initiator)

    return membership, event


def _build_member_added_event(
    group: UserGroup, member: User, occurred_at: datetime, initiator: User
) -> UserGroupMemberAddedEvent:
    return UserGroupMemberAddedEvent(
        occurred_at=occurred_at,
        initiator=initiator,
        group=group,
        member=member,
    )


def remove_member(
    group: UserGroup, membership: UserGroupMembership, initiator: User
) -> UserGroupMemberRemovedEvent:
    """Remove a member from a group."""
    member = membership.user
    occurred_at = datetime.utcnow()

    event = _build_member_removed_event(group, member, occurred_at, initiator)

    return event


def _build_member_removed_event(
    group: UserGroup, member: User, occurred_at: datetime, initiator: User
) -> UserGroupMemberRemovedEvent:
    return UserGroupMemberRemovedEvent(
        occurred_at=occurred_at,
        initiator=initiator,
        group=group,
        member=member,
    )
