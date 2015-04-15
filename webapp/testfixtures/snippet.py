# -*- coding: utf-8 -*-

from byceps.blueprints.snippet.models import CurrentVersionAssociation, \
    Snippet, SnippetVersion


def create_snippet(party, name):
    return Snippet(
        party=party,
        name=name)


def create_snippet_version(snippet, creator, *, created_at=None,
                           title='', body='', image_url_path=None):
    return SnippetVersion(
        snippet=snippet,
        created_at=created_at,
        creator=creator,
        title=title,
        body=body,
        image_url_path=image_url_path)


def create_current_version_association(snippet, version):
    return CurrentVersionAssociation(
        snippet=snippet,
        version=version)
