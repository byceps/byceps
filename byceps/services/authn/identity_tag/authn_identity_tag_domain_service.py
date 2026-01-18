"""
byceps.services.authn.identity_tag.authn_identity_tag_domain_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from byceps.services.authn.events import (
    UserIdentityTagCreatedEvent,
    UserIdentityTagDeletedEvent,
)
from byceps.services.user.log import user_log_domain_service
from byceps.services.user.log.models import UserLogEntry
from byceps.services.user.models.user import User
from byceps.util.uuid import generate_uuid7

from .models import UserIdentityTag


def create_tag(
    creator: User,
    identifier: str,
    user: User,
    *,
    note: str | None = None,
    suspended: bool = False,
) -> tuple[UserIdentityTag, UserIdentityTagCreatedEvent, UserLogEntry]:
    """Create a tag."""
    tag = _build_tag(creator, identifier, user, note, suspended)

    event = _build_tag_created_event(tag)
    log_entry = _build_tag_created_log_entry(event)

    return tag, event, log_entry


def _build_tag(
    creator: User,
    identifier: str,
    user: User,
    note: str | None,
    suspended: bool,
) -> UserIdentityTag:
    return UserIdentityTag(
        id=generate_uuid7(),
        created_at=datetime.utcnow(),
        creator=creator,
        identifier=identifier,
        user=user,
        note=note,
        suspended=suspended,
    )


def _build_tag_created_event(
    tag: UserIdentityTag,
) -> UserIdentityTagCreatedEvent:
    return UserIdentityTagCreatedEvent(
        occurred_at=tag.created_at,
        initiator=tag.creator,
        user=tag.user,
        tag_id=tag.id,
        identifier=tag.identifier,
    )


def _build_tag_created_log_entry(
    event: UserIdentityTagCreatedEvent,
) -> UserLogEntry:
    return user_log_domain_service.build_entry(
        'user-identity-tag-created',
        event.user,
        {'tag_id': str(event.tag_id)},
        occurred_at=event.occurred_at,
        initiator=event.initiator,
    )


def delete_tag(
    tag: UserIdentityTag, initiator: User
) -> tuple[UserIdentityTagDeletedEvent, UserLogEntry]:
    """Delete a tag."""
    occurred_at = datetime.utcnow()

    event = _build_tag_deleted_event(tag, occurred_at, initiator)
    log_entry = _build_tag_deleted_log_entry(event)

    return event, log_entry


def _build_tag_deleted_event(
    tag: UserIdentityTag, occurred_at: datetime, initiator: User
) -> UserIdentityTagDeletedEvent:
    return UserIdentityTagDeletedEvent(
        occurred_at=occurred_at,
        initiator=initiator,
        user=tag.user,
        tag_id=tag.id,
        identifier=tag.identifier,
    )


def _build_tag_deleted_log_entry(
    event: UserIdentityTagDeletedEvent,
) -> UserLogEntry:
    return user_log_domain_service.build_entry(
        'user-identity-tag-deleted',
        event.user,
        {'tag_id': str(event.tag_id)},
        occurred_at=event.occurred_at,
        initiator=event.initiator,
    )
