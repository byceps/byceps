"""
byceps.services.snippet.snippet_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime
from typing import Optional, Sequence

from sqlalchemy import delete, select

from ...database import db
from ...events.snippet import SnippetCreated, SnippetDeleted, SnippetUpdated
from ...services.user.models.user import User
from ...services.user import user_service
from ...typing import UserID

from .dbmodels import (
    DbCurrentSnippetVersionAssociation,
    DbSnippet,
    DbSnippetVersion,
)
from .models import SnippetID, SnippetScope, SnippetVersionID


def create_snippet(
    scope: SnippetScope,
    name: str,
    language_code: str,
    creator_id: UserID,
    body: str,
) -> tuple[DbSnippetVersion, SnippetCreated]:
    """Create a snippet and its initial version, and return that version."""
    creator = user_service.get_user(creator_id)

    snippet = DbSnippet(scope, name, language_code)
    db.session.add(snippet)

    version = DbSnippetVersion(snippet, creator_id, body)
    db.session.add(version)

    current_version_association = DbCurrentSnippetVersionAssociation(
        snippet, version
    )
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
) -> tuple[DbSnippetVersion, SnippetUpdated]:
    """Update snippet with a new version, and return that version."""
    snippet = find_snippet(snippet_id)
    if snippet is None:
        raise ValueError('Unknown snippet ID')

    creator = user_service.get_user(creator_id)

    version = DbSnippetVersion(snippet, creator_id, body)
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

    db_versions = get_versions(snippet_id)

    db.session.execute(
        delete(DbCurrentSnippetVersionAssociation).where(
            DbCurrentSnippetVersionAssociation.snippet_id == snippet_id
        )
    )

    for db_version in db_versions:
        db.session.execute(
            delete(DbSnippetVersion).where(DbSnippetVersion.id == db_version.id)
        )

    db.session.execute(delete(DbSnippet).where(DbSnippet.id == snippet_id))

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
    return db.session.scalars(
        select(DbSnippet).filter(DbSnippet.id.in_(snippet_ids))
    ).all()


def get_snippets_for_scope_with_current_versions(
    scope: SnippetScope,
) -> Sequence[DbSnippet]:
    """Return all snippets with their current versions for that scope."""
    return (
        db.session.scalars(
            select(DbSnippet)
            .filter_by(scope_type=scope.type_)
            .filter_by(scope_name=scope.name)
            .options(
                db.joinedload(DbSnippet.current_version_association).joinedload(
                    DbCurrentSnippetVersionAssociation.version
                )
            )
        )
        .unique()
        .all()
    )


def find_snippet_version(
    version_id: SnippetVersionID,
) -> Optional[DbSnippetVersion]:
    """Return the snippet version with that id, or `None` if not found."""
    return db.session.get(DbSnippetVersion, version_id)


def find_current_version_of_snippet_with_name(
    scope: SnippetScope, name: str, language_code: str
) -> Optional[DbSnippetVersion]:
    """Return the current version of the snippet with that name and
    language code in that scope, or `None` if not found.
    """
    return db.session.scalars(
        select(DbSnippetVersion)
        .join(DbCurrentSnippetVersionAssociation)
        .join(DbSnippet)
        .filter(DbSnippet.scope_type == scope.type_)
        .filter(DbSnippet.scope_name == scope.name)
        .filter(DbSnippet.name == name)
        .filter(DbSnippet.language_code == language_code)
    ).one_or_none()


def get_versions(snippet_id: SnippetID) -> Sequence[DbSnippetVersion]:
    """Return all versions of that snippet, sorted from most recent to
    oldest.
    """
    return db.session.scalars(
        select(DbSnippetVersion)
        .filter_by(snippet_id=snippet_id)
        .order_by(DbSnippetVersion.created_at.desc())
    ).all()


def get_snippet_body(scope: SnippetScope, name: str, language_code: str) -> str:
    """Return the body of the current version of the snippet in that
    scope with that name and language.

    Raise an exception if not found.
    """
    version = find_current_version_of_snippet_with_name(
        scope, name, language_code
    )

    if not version:
        raise SnippetNotFound(scope, name, language_code)

    return version.body.strip()


def search_snippets(
    search_term: str, scope: Optional[SnippetScope]
) -> Sequence[DbSnippetVersion]:
    """Search in (the latest versions of) snippets."""
    stmt = (
        select(DbSnippetVersion)
        .join(DbCurrentSnippetVersionAssociation)
        .join(DbSnippet)
    )

    if scope is not None:
        stmt = stmt.filter(DbSnippet.scope_type == scope.type_).filter(
            DbSnippet.scope_name == scope.name
        )

    stmt = stmt.filter(DbSnippetVersion.body.contains(search_term))

    return db.session.scalars(stmt).all()


class SnippetNotFound(Exception):
    def __init__(
        self, scope: SnippetScope, name: str, language_code: str
    ) -> None:
        self.scope = scope
        self.name = name
        self.language_code = language_code
