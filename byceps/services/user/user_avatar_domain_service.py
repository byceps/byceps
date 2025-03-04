"""
byceps.services.user.user_avatar_domain_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from byceps.services.core.events import EventUser
from byceps.util.uuid import generate_uuid7

from .events import UserAvatarRemovedEvent, UserAvatarUpdatedEvent
from .models.log import UserLogEntry
from .models.user import User, UserAvatar


def update_avatar_image(
    user: User,
    avatar: UserAvatar,
    initiator: User,
) -> tuple[UserAvatarUpdatedEvent, UserLogEntry]:
    """Set a new avatar image for the user."""
    occurred_at = datetime.utcnow()

    event = _build_avatar_updated_event(occurred_at, initiator, user, avatar)

    log_entry = _build_avatar_updated_log_entry(
        occurred_at, user, initiator, avatar
    )

    return event, log_entry


def _build_avatar_updated_event(
    occurred_at: datetime,
    initiator: User,
    user: User,
    avatar: UserAvatar,
) -> UserAvatarUpdatedEvent:
    return UserAvatarUpdatedEvent(
        occurred_at=occurred_at,
        initiator=EventUser.from_user(initiator),
        user=EventUser.from_user(user),
        avatar_id=avatar.id,
    )


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
) -> tuple[UserAvatarRemovedEvent, UserLogEntry]:
    """Remove the user's avatar image."""
    occurred_at = datetime.utcnow()

    event = _build_avatar_removed_event(occurred_at, initiator, user, avatar)

    log_entry = _build_avatar_removed_log_entry(
        occurred_at, user, initiator, avatar
    )

    return event, log_entry


def _build_avatar_removed_event(
    occurred_at: datetime,
    initiator: User,
    user: User,
    avatar: UserAvatar,
) -> UserAvatarRemovedEvent:
    return UserAvatarRemovedEvent(
        occurred_at=occurred_at,
        initiator=EventUser.from_user(initiator),
        user=EventUser.from_user(user),
        avatar_id=avatar.id,
    )


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
