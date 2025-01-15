"""
byceps.services.user_group.user_group_domain_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from byceps.services.party.models import Party
from byceps.services.user.models.user import User
from byceps.util.uuid import generate_uuid7

from .models import UserGroup


def create_group(
    party: Party,
    created_at: datetime,
    creator: User,
    title: str,
    *,
    description: str | None = None,
) -> UserGroup:
    """Create a group."""
    group_id = generate_uuid7()

    return UserGroup(
        id=group_id,
        party_id=party.id,
        created_at=created_at,
        creator=creator,
        title=title,
        description=description,
    )
