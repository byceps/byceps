# -*- coding: utf-8 -*-

"""
testfixtures.snippet
~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.blueprints.snippet.models.snippet import \
    CurrentVersionAssociation, Snippet, SnippetVersion


def create_snippet(party, name):
    return Snippet(
        party=party,
        name=name)


def create_snippet_version(snippet, creator, *, created_at=None,
                           title='', head='', body='', image_url_path=None):
    version = SnippetVersion(
        snippet=snippet,
        creator=creator,
        title=title,
        head=head,
        body=body,
        image_url_path=image_url_path)

    if created_at is not None:
        version.created_at = created_at

    return version

def create_current_version_association(snippet, version):
    return CurrentVersionAssociation(
        snippet=snippet,
        version=version)
