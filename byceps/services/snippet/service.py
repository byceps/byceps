"""
byceps.services.snippet.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import List, Optional, Sequence

from ...database import db
from ...typing import UserID

from .models.snippet import CurrentVersionAssociation, Snippet, SnippetVersion
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
) -> SnippetVersion:
    """Create a document and its initial version, and return that version."""
    return _create_snippet(scope, name, SnippetType.document, creator_id, body,
                           title=title, head=head,
                           image_url_path=image_url_path)


def update_document(
    document: Snippet,
    creator_id: UserID,
    title: str,
    body: str,
    *,
    head: Optional[str] = None,
    image_url_path: Optional[str] = None,
) -> SnippetVersion:
    """Update document with a new version, and return that version."""
    return _update_snippet(document, creator_id, title, head, body,
                           image_url_path)


# -------------------------------------------------------------------- #
# fragment


def create_fragment(
    scope: Scope, name: str, creator_id: UserID, body: str
) -> SnippetVersion:
    """Create a fragment and its initial version, and return that version."""
    return _create_snippet(scope, name, SnippetType.fragment, creator_id, body)


def update_fragment(
    fragment: Snippet, creator_id: UserID, body: str
) -> SnippetVersion:
    """Update fragment with a new version, and return that version."""
    title = None
    head = None
    image_url_path = None

    return _update_snippet(fragment, creator_id, title, head, body,
                           image_url_path)


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
) -> SnippetVersion:
    """Create a snippet and its initial version, and return that version."""
    snippet = Snippet(scope, name, type_)
    db.session.add(snippet)

    version = SnippetVersion(snippet, creator_id, title, head, body,
                             image_url_path)
    db.session.add(version)

    current_version_association = CurrentVersionAssociation(snippet, version)
    db.session.add(current_version_association)

    db.session.commit()

    return version


def _update_snippet(
    snippet: Snippet,
    creator_id: UserID,
    title: Optional[str],
    head: Optional[str],
    body: str,
    image_url_path: Optional[str],
) -> SnippetVersion:
    """Update snippet with a new version, and return that version."""
    version = SnippetVersion(snippet, creator_id, title, head, body,
                             image_url_path)
    db.session.add(version)

    snippet.current_version = version

    db.session.commit()

    return version


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
    except:
        db.session.rollback()
        return False


def find_snippet(snippet_id: SnippetID) -> Optional[Snippet]:
    """Return the snippet with that id, or `None` if not found."""
    return Snippet.query.get(snippet_id)


def get_snippets_for_scope_with_current_versions(
    scope: Scope
) -> Sequence[Snippet]:
    """Return all snippets with their current versions for that scope."""
    return Snippet.query \
        .filter_by(scope_type=scope.type_) \
        .filter_by(scope_name=scope.name) \
        .options(
            db.joinedload('current_version_association').joinedload('version')
        ) \
        .all()


def find_snippet_version(
    version_id: SnippetVersionID
) -> Optional[SnippetVersion]:
    """Return the snippet version with that id, or `None` if not found."""
    return SnippetVersion.query.get(version_id)


def find_current_version_of_snippet_with_name(
    scope: Scope, name: str
) -> SnippetVersion:
    """Return the current version of the snippet with that name in that
    scope, or `None` if not found.
    """
    return SnippetVersion.query \
        .join(CurrentVersionAssociation) \
        .join(Snippet) \
            .filter(Snippet.scope_type == scope.type_) \
            .filter(Snippet.scope_name == scope.name) \
            .filter(Snippet.name == name) \
        .one_or_none()


def get_versions(snippet_id: SnippetID) -> Sequence[SnippetVersion]:
    """Return all versions of that snippet, sorted from most recent to
    oldest.
    """
    return SnippetVersion.query \
        .filter_by(snippet_id=snippet_id) \
        .latest_first() \
        .all()


def search_snippets(
    search_term: str, scope: Optional[Scope]
) -> List[SnippetVersion]:
    """Search in (the latest versions of) snippets."""
    q = SnippetVersion.query \
        .join(CurrentVersionAssociation) \
        .join(Snippet)

    if scope is not None:
        q = q \
            .filter(Snippet.scope_type == scope.type_) \
            .filter(Snippet.scope_name == scope.name)

    return q \
            .filter(
                db.or_(
                    SnippetVersion.title.contains(search_term),
                    SnippetVersion.head.contains(search_term),
                    SnippetVersion.body.contains(search_term),
                    SnippetVersion.image_url_path.contains(search_term),
                )
            ) \
        .all()


class SnippetNotFound(Exception):

    def __init__(self, scope: Scope, name: str) -> None:
        self.scope = scope
        self.name = name
