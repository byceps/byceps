"""
byceps.services.snippet.snippet_repository
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections.abc import Sequence
from datetime import datetime

from sqlalchemy import delete, select

from byceps.database import db
from byceps.services.user.models.user import User, UserID
from byceps.util.result import Err, Ok, Result

from .dbmodels import (
    DbCurrentSnippetVersionAssociation,
    DbSnippet,
    DbSnippetVersion,
)
from .errors import SnippetDeletionFailedError
from .models import SnippetID, SnippetScope, SnippetVersionID


def create_snippet(
    scope: SnippetScope,
    name: str,
    language_code: str,
    created_at: datetime,
    creator_id: UserID,
    body: str,
) -> tuple[DbSnippet, DbSnippetVersion]:
    """Create a snippet and its initial version, and return that version."""
    db_snippet = DbSnippet(scope, name, language_code)
    db.session.add(db_snippet)

    db_version = DbSnippetVersion(db_snippet, created_at, creator_id, body)
    db.session.add(db_version)

    db_current_version_association = DbCurrentSnippetVersionAssociation(
        db_snippet, db_version
    )
    db.session.add(db_current_version_association)

    db.session.commit()

    return db_snippet, db_version


def update_snippet(
    snippet_id: SnippetID, created_at: datetime, creator_id: UserID, body: str
) -> tuple[DbSnippet, DbSnippetVersion]:
    """Update snippet with a new version, and return that version."""
    db_snippet = get_snippet(snippet_id)

    db_version = DbSnippetVersion(db_snippet, created_at, creator_id, body)
    db.session.add(db_version)

    db_snippet.current_version = db_version

    db.session.commit()

    return db_snippet, db_version


def delete_snippet(
    snippet_id: SnippetID, *, initiator: User | None = None
) -> Result[None, SnippetDeletionFailedError]:
    """Delete the snippet and its versions.

    It is expected that no database records (consents, etc.) refer to
    the snippet anymore.
    """
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
        return Err(SnippetDeletionFailedError())

    return Ok(None)


def find_snippet(snippet_id: SnippetID) -> DbSnippet | None:
    """Return the snippet with that id, or `None` if not found."""
    return db.session.get(DbSnippet, snippet_id)


def get_snippet(snippet_id: SnippetID) -> DbSnippet:
    """Return the snippet.

    Raise error if not found.
    """
    db_snippet = find_snippet(snippet_id)

    if db_snippet is None:
        raise ValueError('Unknown snippet ID')

    return db_snippet


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


def get_all_scopes() -> list[SnippetScope]:
    """List all scopes that contain snippets."""
    rows = db.session.execute(
        select(DbSnippet.scope_type, DbSnippet.scope_name).distinct(
            DbSnippet.scope_type, DbSnippet.scope_name
        )
    ).all()

    return [SnippetScope(type_, name) for type_, name in rows]


def find_snippet_version(
    version_id: SnippetVersionID,
) -> DbSnippetVersion | None:
    """Return the snippet version with that id, or `None` if not found."""
    return db.session.get(DbSnippetVersion, version_id)


def find_current_version_of_snippet_with_name(
    scope: SnippetScope, name: str, language_code: str
) -> DbSnippetVersion | None:
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


def search_snippets(
    search_term: str, scope: SnippetScope | None
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
