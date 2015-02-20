# -*- coding: utf-8 -*-

from byceps.blueprints.snippet.models import CurrentVersionAssociation, \
    Snippet, SnippetVersion


def create_snippet(party, name):
    return Snippet(
        party=party,
        name=name)


def create_snippet_version(snippet, creator, *, created_at=None, title='', body=''):
    return SnippetVersion(
        snippet=snippet,
        created_at=created_at,
        creator=creator,
        title=title,
        body=body)


def create_current_version_association(snippet, version):
    return CurrentVersionAssociation(
        snippet=snippet,
        version=version)
