"""
byceps.services.snippet.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from difflib import HtmlDiff
from typing import Optional, Sequence

from ...database import db
from ...typing import PartyID, UserID

from .models.mountpoint import Mountpoint, MountpointID
from .models.snippet import CurrentVersionAssociation, Snippet, SnippetID, \
    SnippetType, SnippetVersion, SnippetVersionID


# -------------------------------------------------------------------- #
# document


def create_document(party_id: PartyID, name: str, creator_id: UserID,
                    title: str, body: str, *, head: Optional[str]=None,
                    image_url_path: Optional[str]=None) -> SnippetVersion:
    """Create a document and its initial version, and return that version."""
    return _create_snippet(party_id, name, SnippetType.document, creator_id,
                           body, title=title, head=head,
                           image_url_path=image_url_path)


def update_document(document: Snippet, creator_id: UserID, title: str,
                    body: str, *, head: Optional[str]=None,
                    image_url_path: Optional[str]=None) -> SnippetVersion:
    """Update document with a new version, and return that version."""
    return _update_snippet(document, creator_id, title, head, body,
                           image_url_path)


# -------------------------------------------------------------------- #
# fragment


def create_fragment(party_id: PartyID, name: str, creator_id: UserID, body: str
                   ) -> SnippetVersion:
    """Create a fragment and its initial version, and return that version."""
    return _create_snippet(party_id, name, SnippetType.fragment, creator_id,
                           body)


def update_fragment(fragment: Snippet, creator_id: UserID, body: str
                   ) -> SnippetVersion:
    """Update fragment with a new version, and return that version."""
    title = None
    head = None
    image_url_path = None

    return _update_snippet(fragment, creator_id, title, head, body,
                           image_url_path)


# -------------------------------------------------------------------- #
# snippet


def _create_snippet(party_id: PartyID, name: str, type_: SnippetType,
                    creator_id: UserID, body: str, *, title: Optional[str]=None,
                    head: Optional[str]=None, image_url_path: Optional[str]=None
                   ) -> SnippetVersion:
    """Create a snippet and its initial version, and return that version."""
    snippet = Snippet(party_id, name, type_)
    db.session.add(snippet)

    version = SnippetVersion(snippet, creator_id, title, head, body,
                             image_url_path)
    db.session.add(version)

    current_version_association = CurrentVersionAssociation(snippet, version)
    db.session.add(current_version_association)

    db.session.commit()

    return version


def _update_snippet(snippet: Snippet, creator_id: UserID, title: Optional[str],
                    head: Optional[str], body: str,
                    image_url_path: Optional[str]) -> SnippetVersion:
    """Update snippet with a new version, and return that version."""
    version = SnippetVersion(snippet, creator_id, title, head, body,
                             image_url_path)
    db.session.add(version)

    snippet.current_version = version

    db.session.commit()

    return version


def find_snippet(snippet_id: SnippetID) -> Optional[Snippet]:
    """Return the snippet with that id, or `None` if not found."""
    return Snippet.query.get(snippet_id)


def get_snippets_for_party_with_current_versions(party_id: PartyID
                                                ) -> Sequence[Snippet]:
    """Return all snippets with their current versions for that party."""
    return Snippet.query \
        .for_party_id(party_id) \
        .options(
            db.joinedload('current_version_association').joinedload('version')
        ) \
        .all()


def find_snippet_version(version_id: SnippetVersionID
                        ) -> Optional[SnippetVersion]:
    """Return the snippet version with that id, or `None` if not found."""
    return SnippetVersion.query.get(version_id)


def find_current_version_of_snippet_with_name(party_id: PartyID, name: str
                                             ) -> SnippetVersion:
    """Return the current version of the snippet with that name for that
    party, or `None` if not found.
    """
    return SnippetVersion.query \
        .join(CurrentVersionAssociation) \
        .join(Snippet) \
            .filter(Snippet.party_id == party_id) \
            .filter(Snippet.name == name) \
        .one_or_none()


class SnippetNotFound(Exception):

    def __init__(self, name: str) -> None:
        self.name = name


def create_html_diff(from_text: str, to_text: str, from_description: str,
                     to_description: str, *, numlines: int=3) -> str:
    """Calculate the difference between the two texts and render it as HTML.

    If the texts to compare are equal, `None` is returned.
    """
    from_text = _fallback_if_none(from_text)
    to_text = _fallback_if_none(to_text)

    if from_text == to_text:
        return None

    from_lines = from_text.split('\n')
    to_lines = to_text.split('\n')

    return HtmlDiff().make_table(from_lines, to_lines,
                                 from_description, to_description,
                                 context=True, numlines=numlines)


def _fallback_if_none(value: Optional[str], *, fallback: str='') -> str:
    return value if (value is not None) else fallback


# -------------------------------------------------------------------- #
# mountpoint


def create_mountpoint(endpoint_suffix: str, url_path: str, snippet: Snippet
                     ) -> Mountpoint:
    """Create a mountpoint."""
    mountpoint = Mountpoint(endpoint_suffix, url_path, snippet)

    db.session.add(mountpoint)
    db.session.commit()

    return mountpoint


def delete_mountpoint(mountpoint: Mountpoint) -> None:
    """Delete the mountpoint."""
    db.session.delete(mountpoint)
    db.session.commit()


def find_mountpoint(mountpoint_id: MountpointID) -> Optional[Mountpoint]:
    """Return the mountpoint with that id, or `None` if not found."""
    return Mountpoint.query.get(mountpoint_id)


def get_mountpoints_for_party(party_id: PartyID) -> Sequence[Mountpoint]:
    """Return all mountpoints for that party."""
    return Mountpoint.query \
        .join(Snippet).filter_by(party_id=party_id) \
        .all()
