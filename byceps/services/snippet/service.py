"""
byceps.services.snippet.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import List, Optional, Sequence, Set, Tuple

from ...database import db
from ...events.snippet import SnippetCreated, SnippetUpdated
from ...typing import UserID

from .models.snippet import (
    CurrentVersionAssociation as DbCurrentVersionAssociation,
    Snippet as DbSnippet,
    SnippetVersion as DbSnippetVersion,
)
from .transfer.models import Scope, SnippetID, SnippetType, SnippetVersionID


# -------------------------------------------------------------------- #
# document


def create_document(
    scope: Scope,
    name: str,
    creator_id: UserID,
    title: str,
    body: str,
    *,
    head: Optional[str] = None,
    image_url_path: Optional[str] = None,
) -> Tuple[DbSnippetVersion, SnippetCreated]:
    """Create a document and its initial version, and return that version."""
    return _create_snippet(
        scope,
        name,
        SnippetType.document,
        creator_id,
        body,
        title=title,
        head=head,
        image_url_path=image_url_path,
    )


def update_document(
    snippet_id: SnippetID,
    creator_id: UserID,
    title: str,
    body: str,
    *,
    head: Optional[str] = None,
    image_url_path: Optional[str] = None,
) -> Tuple[DbSnippetVersion, SnippetUpdated]:
    """Update document with a new version, and return that version."""
    return _update_snippet(
        snippet_id, creator_id, title, head, body, image_url_path
    )


# -------------------------------------------------------------------- #
# fragment


def create_fragment(
    scope: Scope, name: str, creator_id: UserID, body: str
) -> Tuple[DbSnippetVersion, SnippetCreated]:
    """Create a fragment and its initial version, and return that version."""
    return _create_snippet(scope, name, SnippetType.fragment, creator_id, body)


def update_fragment(
    snippet_id: SnippetID, creator_id: UserID, body: str
) -> Tuple[DbSnippetVersion, SnippetUpdated]:
    """Update fragment with a new version, and return that version."""
    title = None
    head = None
    image_url_path = None

    return _update_snippet(
        snippet_id, creator_id, title, head, body, image_url_path
    )


# -------------------------------------------------------------------- #
# snippet


def _create_snippet(
    scope: Scope,
    name: str,
    type_: SnippetType,
    creator_id: UserID,
    body: str,
    *,
    title: Optional[str] = None,
    head: Optional[str] = None,
    image_url_path: Optional[str] = None,
) -> Tuple[DbSnippetVersion, SnippetCreated]:
    """Create a snippet and its initial version, and return that version."""
    snippet = DbSnippet(scope, name, type_)
    db.session.add(snippet)

    version = DbSnippetVersion(
        snippet, creator_id, title, head, body, image_url_path
    )
    db.session.add(version)

    current_version_association = DbCurrentVersionAssociation(snippet, version)
    db.session.add(current_version_association)

    db.session.commit()

    event = SnippetCreated(
        occurred_at=version.created_at, snippet_version_id=version.id
    )

    return version, event


def _update_snippet(
    snippet_id: SnippetID,
    creator_id: UserID,
    title: Optional[str],
    head: Optional[str],
    body: str,
    image_url_path: Optional[str],
) -> Tuple[DbSnippetVersion, SnippetUpdated]:
    """Update snippet with a new version, and return that version."""
    snippet = find_snippet(snippet_id)
    if snippet is None:
        raise ValueError('Unknown snippet ID')

    version = DbSnippetVersion(
        snippet, creator_id, title, head, body, image_url_path
    )
    db.session.add(version)

    snippet.current_version = version

    db.session.commit()

    event = SnippetUpdated(
        occurred_at=version.created_at, snippet_version_id=version.id
    )

    return version, event


def delete_snippet(snippet_id: SnippetID) -> bool:
    """Delete the snippet and its versions.

    It is expected that no database records (mountpoints, consents,
    etc.) refer to the snippet anymore.

    Return `True` on success, or `False` if an error occured.
    """
    snippet = find_snippet(snippet_id)
    if snippet is None:
        raise ValueError('Unknown snippet ID')

    db.session.delete(snippet.current_version_association)

    versions = get_versions(snippet_id)
    for version in versions:
        db.session.delete(version)

    db.session.delete(snippet)

    try:
        db.session.commit()
        return True
    except Exception:
        db.session.rollback()
        return False


def find_snippet(snippet_id: SnippetID) -> Optional[DbSnippet]:
    """Return the snippet with that id, or `None` if not found."""
    return DbSnippet.query.get(snippet_id)


def get_snippets(snippet_ids: Set[SnippetID]) -> Sequence[DbSnippet]:
    """Return these snippets."""
    return DbSnippet.query \
        .filter(DbSnippet.id.in_(snippet_ids)) \
        .all()


def get_snippets_for_scope_with_current_versions(
    scope: Scope
) -> Sequence[DbSnippet]:
    """Return all snippets with their current versions for that scope."""
    return DbSnippet.query \
        .filter_by(scope_type=scope.type_) \
        .filter_by(scope_name=scope.name) \
        .options(
            db.joinedload('current_version_association').joinedload('version')
        ) \
        .all()


def find_snippet_version(
    version_id: SnippetVersionID
) -> Optional[DbSnippetVersion]:
    """Return the snippet version with that id, or `None` if not found."""
    return DbSnippetVersion.query.get(version_id)


def find_current_version_of_snippet_with_name(
    scope: Scope, name: str
) -> DbSnippetVersion:
    """Return the current version of the snippet with that name in that
    scope, or `None` if not found.
    """
    return DbSnippetVersion.query \
        .join(DbCurrentVersionAssociation) \
        .join(DbSnippet) \
            .filter(DbSnippet.scope_type == scope.type_) \
            .filter(DbSnippet.scope_name == scope.name) \
            .filter(DbSnippet.name == name) \
        .one_or_none()


def get_versions(snippet_id: SnippetID) -> Sequence[DbSnippetVersion]:
    """Return all versions of that snippet, sorted from most recent to
    oldest.
    """
    return DbSnippetVersion.query \
        .filter_by(snippet_id=snippet_id) \
        .latest_first() \
        .all()


def search_snippets(
    search_term: str, scope: Optional[Scope]
) -> List[DbSnippetVersion]:
    """Search in (the latest versions of) snippets."""
    q = DbSnippetVersion.query \
        .join(DbCurrentVersionAssociation) \
        .join(DbSnippet)

    if scope is not None:
        q = q \
            .filter(DbSnippet.scope_type == scope.type_) \
            .filter(DbSnippet.scope_name == scope.name)

    return q \
            .filter(
                db.or_(
                    DbSnippetVersion.title.contains(search_term),
                    DbSnippetVersion.head.contains(search_term),
                    DbSnippetVersion.body.contains(search_term),
                    DbSnippetVersion.image_url_path.contains(search_term),
                )
            ) \
        .all()


class SnippetNotFound(Exception):

    def __init__(self, scope: Scope, name: str) -> None:
        self.scope = scope
        self.name = name
