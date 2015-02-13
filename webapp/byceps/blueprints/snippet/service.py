# -*- coding: utf-8 -*-

"""
byceps.blueprints.snippet.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2015 Jochen Kupperschmidt
"""

from flask import g

from .models import Snippet, SnippetVersion


def find_latest_version_of_snippet(name):
    """Return the latest version of the snippet with that name."""
    latest_version = SnippetVersion.query \
        .join(Snippet) \
            .filter(Snippet.party == g.party) \
            .filter(Snippet.name == name) \
        .latest_first() \
        .first()

    if latest_version is None:
        raise SnippetNotFound(name)

    return latest_version


class SnippetNotFound(Exception):

    def __init__(self, name):
        self.name = name
