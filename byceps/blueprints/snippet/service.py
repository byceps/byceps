# -*- coding: utf-8 -*-

"""
byceps.blueprints.snippet.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from sqlalchemy.orm.exc import NoResultFound

from ...database import db

from .models.mountpoint import Mountpoint
from .models.snippet import CurrentVersionAssociation, Snippet, SnippetVersion


def create_snippet(party, name, creator, title, head, body, image_url_path):
    """Create a snippet and its initial version, and return that version."""
    snippet = Snippet(party, name)
    db.session.add(snippet)

    version = SnippetVersion(snippet, creator, title, head, body,
                             image_url_path)
    db.session.add(version)

    current_version_association = CurrentVersionAssociation(snippet, version)
    db.session.add(current_version_association)

    db.session.commit()

    return version


def update_snippet(snippet, creator, title, head, body, image_url_path):
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
        .for_party(party) \
        .all()


class SnippetNotFound(Exception):

    def __init__(self, name):
        self.name = name
