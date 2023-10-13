"""
byceps.services.authn.identity_tag.authn_identity_tag_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2022-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import delete, select

from byceps.database import db
from byceps.services.user import user_log_service, user_service
from byceps.services.user.models.log import UserLogEntry
from byceps.services.user.models.user import User

from . import authn_identity_tag_domain_service
from .dbmodels import DbUserIdentityTag
from .models import UserIdentityTag


def create_tag(
    creator: User,
    identifier: str,
    user: User,
    *,
    note: str | None = None,
    suspended: bool = False,
) -> UserIdentityTag:
    """Create a tag."""
    tag, event, log_entry = authn_identity_tag_domain_service.create_tag(
        creator, identifier, user, note=note, suspended=suspended
    )

    _persist_tag_creation(tag, log_entry)

    return tag


def _persist_tag_creation(
    tag: UserIdentityTag, log_entry: UserLogEntry
) -> None:
    db_tag = DbUserIdentityTag(
        tag.id,
        tag.created_at,
        tag.creator.id,
        tag.identifier,
        tag.user.id,
        tag.note,
        tag.suspended,
    )
    db.session.add(db_tag)

    db_log_entry = user_log_service.to_db_entry(log_entry)
    db.session.add(db_log_entry)

    db.session.commit()


def delete_tag(tag: UserIdentityTag, initiator: User) -> None:
    """Delete a tag."""
    event, log_entry = authn_identity_tag_domain_service.delete_tag(
        tag, initiator
    )

    db.session.execute(
        delete(DbUserIdentityTag).where(DbUserIdentityTag.id == tag.id)
    )

    db_log_entry = user_log_service.to_db_entry(log_entry)
    db.session.add(db_log_entry)

    db.session.commit()


def find_tag(tag_id: UUID) -> UserIdentityTag | None:
    """Return the tag, if found."""
    db_tag = db.session.execute(
        select(DbUserIdentityTag).filter_by(id=tag_id)
    ).scalar_one_or_none()

    if db_tag is None:
        return None

    creator = user_service.get_user(db_tag.creator_id, include_avatar=True)
    user = user_service.get_user(db_tag.user_id, include_avatar=True)

    return _db_entity_to_tag(db_tag, creator, user)


def find_tag_by_identifier(identifier: str) -> UserIdentityTag | None:
    """Return the tag with this identifier."""
    db_tag = db.session.scalars(
        select(DbUserIdentityTag).filter(
            db.func.lower(DbUserIdentityTag.identifier) == identifier.lower()
        )
    ).one_or_none()

    if db_tag is None:
        return None

    creator = user_service.get_user(db_tag.creator_id, include_avatar=True)
    user = user_service.get_user(db_tag.user_id, include_avatar=True)

    return _db_entity_to_tag(db_tag, creator, user)


def get_all_tags() -> list[UserIdentityTag]:
    """Return all tags."""
    db_tags = db.session.scalars(select(DbUserIdentityTag)).all()

    creator_ids = {db_tag.creator_id for db_tag in db_tags}
    user_ids = {db_tag.user_id for db_tag in db_tags}
    creator_and_user_ids = user_ids.union(creator_ids)
    creators_and_users_by_id = user_service.get_users_indexed_by_id(
        creator_and_user_ids, include_avatars=True
    )

    return [
        _db_entity_to_tag(
            db_tag,
            creators_and_users_by_id[db_tag.creator_id],
            creators_and_users_by_id[db_tag.user_id],
        )
        for db_tag in db_tags
    ]


def _db_entity_to_tag(
    db_tag: DbUserIdentityTag, creator: User, user: User
) -> UserIdentityTag:
    return UserIdentityTag(
        id=db_tag.id,
        created_at=db_tag.created_at,
        creator=creator,
        identifier=db_tag.identifier,
        user=user,
        note=db_tag.note,
        suspended=db_tag.suspended,
    )
