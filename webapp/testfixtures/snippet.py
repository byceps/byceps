# -*- coding: utf-8 -*-

from byceps.blueprints.snippet.models import Snippet, SnippetVersion


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
