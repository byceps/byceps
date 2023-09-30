"""
byceps.services.authn.identity_tag.authn_identity_tag_domain_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2022-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from datetime import datetime

from byceps.events.authn import UserIdentityTagCreatedEvent
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
        initiator_id=tag.creator.id,
        initiator_screen_name=tag.creator.screen_name,
        identifier=tag.identifier,
        user_id=tag.user.id,
        user_screen_name=tag.user.screen_name,
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
