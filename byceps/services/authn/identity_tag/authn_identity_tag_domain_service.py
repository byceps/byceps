"""
byceps.services.authn.identity_tag.authn_identity_tag_domain_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2022-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from datetime import datetime

from byceps.events.authn import (
    UserIdentityTagCreatedEvent,
    UserIdentityTagDeletedEvent,
)
from byceps.services.user.models.log import UserLogEntry
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
    log_entry = _build_tag_created_log_entry(tag)

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
        identifier=tag.identifier,
        user=tag.user,
    )


def _build_tag_created_log_entry(tag: UserIdentityTag) -> UserLogEntry:
    return UserLogEntry(
        id=generate_uuid7(),
        occurred_at=tag.created_at,
        event_type='user-identity-tag-created',
        user_id=tag.user.id,
        initiator_id=tag.creator.id,
        data={'tag_id': str(tag.id)},
    )


def delete_tag(
    tag: UserIdentityTag, initiator: User
) -> tuple[UserIdentityTagDeletedEvent, UserLogEntry]:
    """Delete a tag."""
    occurred_at = datetime.utcnow()

    event = _build_tag_deleted_event(tag, occurred_at, initiator)
    log_entry = _build_tag_deleted_log_entry(tag, occurred_at, initiator)

    return event, log_entry


def _build_tag_deleted_event(
    tag: UserIdentityTag, occurred_at: datetime, initiator: User
) -> UserIdentityTagDeletedEvent:
    return UserIdentityTagDeletedEvent(
        occurred_at=occurred_at,
        initiator=initiator,
        identifier=tag.identifier,
        user=tag.user,
    )


def _build_tag_deleted_log_entry(
    tag: UserIdentityTag, occurred_at: datetime, initiator: User
) -> UserLogEntry:
    return UserLogEntry(
        id=generate_uuid7(),
        occurred_at=occurred_at,
        event_type='user-identity-tag-deleted',
        user_id=tag.user.id,
        initiator_id=initiator.id,
        data={'tag_id': str(tag.id)},
    )
