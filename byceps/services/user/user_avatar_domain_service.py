"""
byceps.services.user.user_avatar_domain_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from byceps.services.user.log import user_log_domain_service
from byceps.services.user.log.models import UserLogEntry

from .events import UserAvatarRemovedEvent, UserAvatarUpdatedEvent
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
        initiator=initiator,
        user=user,
        avatar_id=avatar.id,
    )


def _build_avatar_updated_log_entry(
    occurred_at: datetime,
    user: User,
    initiator: User,
    avatar: UserAvatar,
) -> UserLogEntry:
    return user_log_domain_service.build_entry(
        'user-avatar-updated',
        user,
        {
            'avatar_id': str(avatar.id),
            'filename': str(avatar.filename),
        },
        occurred_at=occurred_at,
        initiator=initiator,
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
        initiator=initiator,
        user=user,
        avatar_id=avatar.id,
    )


def _build_avatar_removed_log_entry(
    occurred_at: datetime,
    user: User,
    initiator: User,
    avatar: UserAvatar,
) -> UserLogEntry:
    return user_log_domain_service.build_entry(
        'user-avatar-removed',
        user,
        {
            'avatar_id': str(avatar.id),
            'filename': str(avatar.filename),
        },
        occurred_at=occurred_at,
        initiator=initiator,
    )
