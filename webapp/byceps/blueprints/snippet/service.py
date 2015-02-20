# -*- coding: utf-8 -*-

"""
byceps.blueprints.snippet.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2015 Jochen Kupperschmidt
"""

from .models import Snippet


def get_current_version_of_snippet_with_name(name):
    """Return the current version of the snippet with that name."""
    snippet = get_snippet_by_name(name)
    return snippet.current_version


def get_snippet_by_name(name):
    """Return the snippet with that name."""
    snippet = Snippet.query \
        .for_current_party() \
        .filter_by(name=name) \
        .first()

    if snippet is None:
        raise SnippetNotFound(name)

    return snippet


class SnippetNotFound(Exception):

    def __init__(self, name):
        self.name = name
