# -*- coding: utf-8 -*-

"""
byceps.blueprints.snippet.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2015 Jochen Kupperschmidt
"""

from .models import Snippet, SnippetVersion


def find_latest_version_of_snippet(name):
    """Return the latest version of the snippet with that name."""
    latest_version = SnippetVersion.query \
        .join(Snippet).filter(Snippet.name == name) \
        .latest_first() \
        .first()

    if latest_version is None:
        raise SnippetNotFound()

    return latest_version


class SnippetNotFound(Exception):
    pass
