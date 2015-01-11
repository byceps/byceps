# -*- coding: utf-8 -*-

"""
byceps.blueprints.snippet.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2015 Jochen Kupperschmidt
"""

from .models import Snippet, SnippetVersion


def find_latest_version_of_snippet(name):
    """Return the latest version of the snippet with that name."""
    return SnippetVersion.query \
        .join(Snippet).filter(Snippet.name == name) \
        .latest_first() \
        .one()
