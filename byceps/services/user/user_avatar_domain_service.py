"""
byceps.services.user.user_avatar_domain_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2024 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime, UTC

from byceps.util.uuid import generate_uuid7

from .models.log import UserLogEntry
from .models.user import User, UserAvatar


def update_avatar_image(
    user: User,
    avatar: UserAvatar,
    initiator: User,
) -> UserLogEntry:
    """Set a new avatar image for the user."""
    occurred_at = datetime.now(UTC)

    log_entry = _build_avatar_updated_log_entry(
        occurred_at, user, initiator, avatar
    )

    return log_entry


def _build_avatar_updated_log_entry(
    occurred_at: datetime,
    user: User,
    initiator: User,
    avatar: UserAvatar,
) -> UserLogEntry:
    return UserLogEntry(
        id=generate_uuid7(),
        occurred_at=occurred_at,
        event_type='user-avatar-updated',
        user_id=user.id,
        initiator_id=initiator.id,
        data={
            'avatar_id': str(avatar.id),
            'filename': str(avatar.filename),
        },
    )


def remove_avatar_image(
    user: User, avatar: UserAvatar, initiator: User
) -> UserLogEntry:
    """Remove the user's avatar image."""
    occurred_at = datetime.now(UTC)

    log_entry = _build_avatar_removed_log_entry(
        occurred_at, user, initiator, avatar
    )

    return log_entry


def _build_avatar_removed_log_entry(
    occurred_at: datetime,
    user: User,
    initiator: User,
    avatar: UserAvatar,
) -> UserLogEntry:
    return UserLogEntry(
        id=generate_uuid7(),
        occurred_at=occurred_at,
        event_type='user-avatar-removed',
        user_id=user.id,
        initiator_id=initiator.id,
        data={
            'avatar_id': str(avatar.id),
            'filename': str(avatar.filename),
        },
    )
