"""
byceps.services.snippet.snippet_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections.abc import Sequence
from datetime import datetime

from sqlalchemy import delete, select

from byceps.database import db
from byceps.services.core.events import EventUser
from byceps.services.user import user_service
from byceps.services.user.models.user import User
from byceps.util.result import Err, Ok, Result

from .dbmodels import (
    DbCurrentSnippetVersionAssociation,
    DbSnippet,
    DbSnippetVersion,
)
from .errors import SnippetAlreadyExistsError, SnippetNotFoundError
from .events import (
    SnippetCreatedEvent,
    SnippetDeletedEvent,
    SnippetUpdatedEvent,
)
from .models import SnippetID, SnippetScope, SnippetVersionID


def copy_snippet(
    source_scope: SnippetScope,
    target_scope: SnippetScope,
    name: str,
    language_code: str,
) -> Result[
    tuple[DbSnippetVersion, SnippetCreatedEvent],
    SnippetAlreadyExistsError | SnippetNotFoundError,
]:
    """Copy a snippet from one scope to another."""
    version = find_current_version_of_snippet_with_name(
        source_scope, name, language_code
    )
    if version is None:
        return Err(
            SnippetNotFoundError(
                scope=source_scope, name=name, language_code=language_code
            )
        )

    target_version = find_current_version_of_snippet_with_name(
        target_scope, name, language_code
    )
    if target_version is not None:
        return Err(
            SnippetAlreadyExistsError(
                scope=source_scope, name=name, language_code=language_code
            )
        )

    creator = user_service.get_user(version.creator_id)

    db_version, event = create_snippet(
        target_scope,
        version.snippet.name,
        version.snippet.language_code,
        creator,
        version.body,
    )

    return Ok((db_version, event))


def create_snippet(
    scope: SnippetScope,
    name: str,
    language_code: str,
    creator: User,
    body: str,
) -> tuple[DbSnippetVersion, SnippetCreatedEvent]:
    """Create a snippet and its initial version, and return that version."""
    snippet = DbSnippet(scope, name, language_code)
    db.session.add(snippet)

    version = DbSnippetVersion(snippet, creator.id, body)
    db.session.add(version)

    current_version_association = DbCurrentSnippetVersionAssociation(
        snippet, version
    )
    db.session.add(current_version_association)

    db.session.commit()

    event = SnippetCreatedEvent(
        occurred_at=version.created_at,
        initiator=EventUser.from_user(creator),
        snippet_id=snippet.id,
        scope=snippet.scope,
        snippet_name=snippet.name,
        language_code=snippet.language_code,
        snippet_version_id=version.id,
    )

    return version, event


def update_snippet(
    snippet_id: SnippetID, creator: User, body: str
) -> tuple[DbSnippetVersion, SnippetUpdatedEvent]:
    """Update snippet with a new version, and return that version."""
    snippet = find_snippet(snippet_id)
    if snippet is None:
        raise ValueError('Unknown snippet ID')

    version = DbSnippetVersion(snippet, creator.id, body)
    db.session.add(version)

    snippet.current_version = version

    db.session.commit()

    event = SnippetUpdatedEvent(
        occurred_at=version.created_at,
        initiator=EventUser.from_user(creator),
        snippet_id=snippet.id,
        scope=snippet.scope,
        snippet_name=snippet.name,
        language_code=snippet.language_code,
        snippet_version_id=version.id,
    )

    return version, event


def delete_snippet(
    snippet_id: SnippetID, *, initiator: User | None = None
) -> tuple[bool, SnippetDeletedEvent | None]:
    """Delete the snippet and its versions.

    It is expected that no database records (consents, etc.) refer to
    the snippet anymore.

    Return `True` on success, or `False` if an error occurred.
    """
    snippet = find_snippet(snippet_id)
    if snippet is None:
        raise ValueError('Unknown snippet ID')

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

    event = SnippetDeletedEvent(
        occurred_at=datetime.utcnow(),
        initiator=EventUser.from_user(initiator) if initiator else None,
        snippet_id=snippet_id,
        scope=scope,
        snippet_name=snippet_name,
        language_code=snippet.language_code,
    )

    return True, event


def find_snippet(snippet_id: SnippetID) -> DbSnippet | None:
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


def get_snippet_body(
    scope: SnippetScope, name: str, language_code: str
) -> Result[str, SnippetNotFoundError]:
    """Return the body of the current version of the snippet in that
    scope with that name and language.
    """
    version = find_current_version_of_snippet_with_name(
        scope, name, language_code
    )

    if not version:
        return Err(SnippetNotFoundError(scope, name, language_code))

    return Ok(version.body.strip())


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
