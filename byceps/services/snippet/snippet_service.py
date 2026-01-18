"""
byceps.services.snippet.snippet_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from byceps.services.user import user_service
from byceps.services.user.models.user import User
from byceps.util.result import Err, Ok, Result

from . import snippet_repository
from .dbmodels import DbSnippet, DbSnippetVersion
from .errors import (
    SnippetAlreadyExistsError,
    SnippetDeletionFailedError,
    SnippetNotFoundError,
)
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
    created_at = datetime.utcnow()

    db_snippet, db_version = snippet_repository.create_snippet(
        scope, name, language_code, created_at, creator.id, body
    )

    event = SnippetCreatedEvent(
        occurred_at=db_version.created_at,
        initiator=creator,
        snippet_id=db_snippet.id,
        scope=db_snippet.scope,
        snippet_name=db_snippet.name,
        language_code=db_snippet.language_code,
        snippet_version_id=db_version.id,
    )

    return db_version, event


def update_snippet(
    snippet_id: SnippetID, creator: User, body: str
) -> tuple[DbSnippetVersion, SnippetUpdatedEvent]:
    """Update snippet with a new version, and return that version."""
    created_at = datetime.utcnow()

    db_snippet, db_version = snippet_repository.update_snippet(
        snippet_id, created_at, creator.id, body
    )

    event = SnippetUpdatedEvent(
        occurred_at=db_version.created_at,
        initiator=creator,
        snippet_id=db_snippet.id,
        scope=db_snippet.scope,
        snippet_name=db_snippet.name,
        language_code=db_snippet.language_code,
        snippet_version_id=db_version.id,
    )

    return db_version, event


def delete_snippet(
    snippet_id: SnippetID, *, initiator: User | None = None
) -> Result[SnippetDeletedEvent, SnippetDeletionFailedError]:
    """Delete the snippet and its versions.

    It is expected that no database records (consents, etc.) refer to
    the snippet anymore.
    """
    db_snippet = snippet_repository.get_snippet(snippet_id)

    # Keep values for use after snippet is deleted.
    snippet_name = db_snippet.name
    scope = db_snippet.scope
    language_code = db_snippet.language_code

    match snippet_repository.delete_snippet(snippet_id):
        case Err(e):
            return Err(e)

    event = SnippetDeletedEvent(
        occurred_at=datetime.utcnow(),
        initiator=initiator,
        snippet_id=snippet_id,
        scope=scope,
        snippet_name=snippet_name,
        language_code=language_code,
    )

    return Ok(event)


def find_snippet(snippet_id: SnippetID) -> DbSnippet | None:
    """Return the snippet with that id, or `None` if not found."""
    return snippet_repository.find_snippet(snippet_id)


def get_snippets(snippet_ids: set[SnippetID]) -> list[DbSnippet]:
    """Return these snippets."""
    db_snippets = snippet_repository.get_snippets(snippet_ids)

    return list(db_snippets)


def get_snippets_for_scope_with_current_versions(
    scope: SnippetScope,
) -> list[DbSnippet]:
    """Return all snippets with their current versions for that scope."""
    db_snippets = (
        snippet_repository.get_snippets_for_scope_with_current_versions(scope)
    )

    return list(db_snippets)


def get_all_scopes() -> list[SnippetScope]:
    """List all scopes that contain snippets."""
    return snippet_repository.get_all_scopes()


def find_snippet_version(
    version_id: SnippetVersionID,
) -> DbSnippetVersion | None:
    """Return the snippet version with that id, or `None` if not found."""
    return snippet_repository.find_snippet_version(version_id)


def find_current_version_of_snippet_with_name(
    scope: SnippetScope, name: str, language_code: str
) -> DbSnippetVersion | None:
    """Return the current version of the snippet with that name and
    language code in that scope, or `None` if not found.
    """
    return snippet_repository.find_current_version_of_snippet_with_name(
        scope, name, language_code
    )


def get_versions(snippet_id: SnippetID) -> list[DbSnippetVersion]:
    """Return all versions of that snippet, sorted from most recent to
    oldest.
    """
    db_versions = snippet_repository.get_versions(snippet_id)

    return list(db_versions)


def get_snippet_body(
    scope: SnippetScope, name: str, language_code: str
) -> Result[str, SnippetNotFoundError]:
    """Return the body of the current version of the snippet in that
    scope with that name and language.
    """
    db_version = find_current_version_of_snippet_with_name(
        scope, name, language_code
    )

    if not db_version:
        return Err(SnippetNotFoundError(scope, name, language_code))

    return Ok(db_version.body.strip())


def search_snippets(
    search_term: str, scope: SnippetScope | None
) -> list[DbSnippetVersion]:
    """Search in (the latest versions of) snippets."""
    db_versions = snippet_repository.search_snippets(search_term, scope)

    return list(db_versions)
