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

from .models import UserGroup, UserGroupMembership


# -------------------------------------------------------------------- #
# groups


def create_group(
    party: Party,
    creator: User,
    title: str,
    *,
    description: str | None = None,
) -> UserGroup:
    """Create a group."""
    group_id = generate_uuid7()
    created_at = datetime.utcnow()

    return UserGroup(
        id=group_id,
        party_id=party.id,
        created_at=created_at,
        creator=creator,
        title=title,
        description=description,
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


# -------------------------------------------------------------------- #
# memberships


def add_member(group: UserGroup, user: User) -> UserGroupMembership:
    """Add a user to a group."""
    membership_id = generate_uuid7()
    created_at = datetime.utcnow()

    return UserGroupMembership(
        id=membership_id,
        created_at=created_at,
        group_id=group.id,
        user=user,
    )
