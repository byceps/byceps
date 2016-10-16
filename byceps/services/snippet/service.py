# -*- coding: utf-8 -*-

"""
byceps.services.snippet.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from difflib import HtmlDiff

from sqlalchemy.orm.exc import NoResultFound

from ...database import db

from .models.mountpoint import Mountpoint
from .models.snippet import CurrentVersionAssociation, Snippet, SnippetType, \
    SnippetVersion


# -------------------------------------------------------------------- #
# snippet


def create_document(party_id, name, creator, title, head, body, image_url_path):
    """Create a document and its initial version, and return that version."""
    return _create_snippet(party_id, name, SnippetType.document, creator, body,
                           title=title, head=head,
                           image_url_path=image_url_path)


def create_fragment(party_id, name, creator, body):
    """Create a fragment and its initial version, and return that version."""
    return _create_snippet(party_id, name, SnippetType.fragment, creator, body)


def _create_snippet(party_id, name, type_, creator, body, *, title=None,
                    head=None, image_url_path=None):
    """Create a snippet and its initial version, and return that version."""
    snippet = Snippet(party_id, name, type_)
    db.session.add(snippet)

    version = SnippetVersion(snippet, creator, title, head, body,
                             image_url_path)
    db.session.add(version)

    current_version_association = CurrentVersionAssociation(snippet, version)
    db.session.add(current_version_association)

    db.session.commit()

    return version


def update_document(document, creator, title, head, body, image_url_path):
    """Update document with a new version, and return that version."""
    return _update_snippet(document, creator, title, head, body, image_url_path)


def update_fragment(fragment, creator, body):
    """Update fragment with a new version, and return that version."""
    title = None
    head = None
    image_url_path = None

    return _update_snippet(fragment, creator, title, head, body, image_url_path)


def _update_snippet(snippet, creator, title, head, body, image_url_path):
    """Update snippet with a new version, and return that version."""
    version = SnippetVersion(snippet, creator, title, head, body,
                             image_url_path)
    db.session.add(version)

    snippet.current_version = version

    db.session.commit()

    return version


def find_snippet(snippet_id):
    """Return the snippet with that id, or `None` if not found."""
    return Snippet.query.get(snippet_id)


def get_documents_for_party(party):
    """Return all documents for that party."""
    return Snippet.query \
        .for_party_id(party.id) \
        .filter_by(_type=SnippetType.document.name) \
        .order_by(Snippet.name) \
        .all()


def get_snippets_for_party_with_current_versions(party):
    """Return all snippets with their current versions for that party."""
    return Snippet.query \
        .for_party_id(party.id) \
        .options(
            db.joinedload('current_version_association').joinedload('version')
        ) \
        .all()


def find_snippet_version(version_id):
    """Return the snippet version with that id, or `None` if not found."""
    return SnippetVersion.query.get(version_id)


def get_current_version_of_snippet_with_name(party, name):
    """Return the current version of the snippet with that name for that
    party.
    """
    try:
        return SnippetVersion.query \
            .join(CurrentVersionAssociation) \
            .join(Snippet) \
                .filter(Snippet.party == party) \
                .filter(Snippet.name == name) \
            .one()
    except NoResultFound:
        raise SnippetNotFound(name)


class SnippetNotFound(Exception):

    def __init__(self, name):
        self.name = name


def create_html_diff(from_text, to_text, from_description, to_description,
                     *, numlines=3):
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


def _fallback_if_none(value, fallback=''):
    return value if (value is not None) else fallback


# -------------------------------------------------------------------- #
# mountpoint


def create_mountpoint(endpoint_suffix, url_path, snippet):
    """Create a mountpoint."""
    mountpoint = Mountpoint(endpoint_suffix, url_path, snippet)

    db.session.add(mountpoint)
    db.session.commit()

    return mountpoint


def delete_mountpoint(mountpoint):
    """Delete the mountpoint."""
    db.session.delete(mountpoint)
    db.session.commit()


def find_mountpoint(mountpoint_id):
    """Return the mountpoint with that id, or `None` if not found."""
    return Mountpoint.query.get(mountpoint_id)


def get_mountpoints_for_party(party):
    """Return all mountpoints for that party."""
    return Mountpoint.query \
        .join(Snippet).filter_by(party_id=party.id) \
        .for_party_id(party.id) \
        .all()
