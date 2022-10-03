"""
byceps.services.snippet.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from datetime import datetime
from typing import Optional, Sequence

from ...database import db
from ...events.snippet import SnippetCreated, SnippetDeleted, SnippetUpdated
from ...services.user import service as user_service
from ...services.user.transfer.models import User
from ...typing import UserID

from .dbmodels.snippet import DbCurrentVersionAssociation, DbSnippet, DbVersion
from .transfer.models import Scope, SnippetID, SnippetVersionID


def create_snippet(
    scope: Scope, name: str, creator_id: UserID, body: str
) -> tuple[DbVersion, SnippetCreated]:
    """Create a snippet and its initial version, and return that version."""
    creator = user_service.get_user(creator_id)

    snippet = DbSnippet(scope, name)
    db.session.add(snippet)

    version = DbVersion(snippet, creator_id, body)
    db.session.add(version)

    current_version_association = DbCurrentVersionAssociation(snippet, version)
    db.session.add(current_version_association)

    db.session.commit()

    event = SnippetCreated(
        occurred_at=version.created_at,
        initiator_id=creator.id,
        initiator_screen_name=creator.screen_name,
        snippet_id=snippet.id,
        scope=snippet.scope,
        snippet_name=snippet.name,
        snippet_version_id=version.id,
    )

    return version, event


def update_snippet(
    snippet_id: SnippetID, creator_id: UserID, body: str
) -> tuple[DbVersion, SnippetUpdated]:
    """Update snippet with a new version, and return that version."""
    snippet = find_snippet(snippet_id)
    if snippet is None:
        raise ValueError('Unknown snippet ID')

    creator = user_service.get_user(creator_id)

    version = DbVersion(snippet, creator_id, body)
    db.session.add(version)

    snippet.current_version = version

    db.session.commit()

    event = SnippetUpdated(
        occurred_at=version.created_at,
        initiator_id=creator.id,
        initiator_screen_name=creator.screen_name,
        snippet_id=snippet.id,
        scope=snippet.scope,
        snippet_name=snippet.name,
        snippet_version_id=version.id,
    )

    return version, event


def delete_snippet(
    snippet_id: SnippetID, *, initiator_id: Optional[UserID] = None
) -> tuple[bool, Optional[SnippetDeleted]]:
    """Delete the snippet and its versions.

    It is expected that no database records (consents, etc.) refer to
    the snippet anymore.

    Return `True` on success, or `False` if an error occurred.
    """
    snippet = find_snippet(snippet_id)
    if snippet is None:
        raise ValueError('Unknown snippet ID')

    initiator: Optional[User]
    if initiator_id is not None:
        initiator = user_service.get_user(initiator_id)
    else:
        initiator = None

    # Keep values for use after snippet is deleted.
    snippet_name = snippet.name
    scope = snippet.scope

    db.session.delete(snippet.current_version_association)

    versions = get_versions(snippet_id)
    for version in versions:
        db.session.delete(version)

    db.session.delete(snippet)

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return False, None

    event = SnippetDeleted(
        occurred_at=datetime.utcnow(),
        initiator_id=initiator.id if initiator else None,
        initiator_screen_name=initiator.screen_name if initiator else None,
        snippet_id=snippet_id,
        scope=scope,
        snippet_name=snippet_name,
    )

    return True, event


def find_snippet(snippet_id: SnippetID) -> Optional[DbSnippet]:
    """Return the snippet with that id, or `None` if not found."""
    return db.session.get(DbSnippet, snippet_id)


def get_snippets(snippet_ids: set[SnippetID]) -> Sequence[DbSnippet]:
    """Return these snippets."""
    return db.session \
        .query(DbSnippet) \
        .filter(DbSnippet.id.in_(snippet_ids)) \
        .all()


def get_snippets_for_scope_with_current_versions(
    scope: Scope,
) -> Sequence[DbSnippet]:
    """Return all snippets with their current versions for that scope."""
    return db.session \
        .query(DbSnippet) \
        .filter_by(scope_type=scope.type_) \
        .filter_by(scope_name=scope.name) \
        .options(
            db.joinedload(DbSnippet.current_version_association)
                .joinedload(DbCurrentVersionAssociation.version)
        ) \
        .all()


def find_snippet_version(version_id: SnippetVersionID) -> Optional[DbVersion]:
    """Return the snippet version with that id, or `None` if not found."""
    return db.session.get(DbVersion, version_id)


def find_current_version_of_snippet_with_name(
    scope: Scope, name: str
) -> DbVersion:
    """Return the current version of the snippet with that name in that
    scope, or `None` if not found.
    """
    return db.session \
        .query(DbVersion) \
        .join(DbCurrentVersionAssociation) \
        .join(DbSnippet) \
            .filter(DbSnippet.scope_type == scope.type_) \
            .filter(DbSnippet.scope_name == scope.name) \
            .filter(DbSnippet.name == name) \
        .one_or_none()


def get_versions(snippet_id: SnippetID) -> Sequence[DbVersion]:
    """Return all versions of that snippet, sorted from most recent to
    oldest.
    """
    return db.session \
        .query(DbVersion) \
        .filter_by(snippet_id=snippet_id) \
        .order_by(DbVersion.created_at.desc()) \
        .all()


def search_snippets(
    search_term: str, scope: Optional[Scope]
) -> list[DbVersion]:
    """Search in (the latest versions of) snippets."""
    q = db.session \
        .query(DbVersion) \
        .join(DbCurrentVersionAssociation) \
        .join(DbSnippet)

    if scope is not None:
        q = q \
            .filter(DbSnippet.scope_type == scope.type_) \
            .filter(DbSnippet.scope_name == scope.name)

    return q \
            .filter(DbVersion.body.contains(search_term)) \
        .all()


class SnippetNotFound(Exception):
    def __init__(self, scope: Scope, name: str) -> None:
        self.scope = scope
        self.name = name
