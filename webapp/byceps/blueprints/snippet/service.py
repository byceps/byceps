# -*- coding: utf-8 -*-

"""
byceps.blueprints.snippet.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from flask import g
from sqlalchemy.orm.exc import NoResultFound

from .models.snippet import CurrentVersionAssociation, Snippet, SnippetVersion


def get_current_version_of_snippet_with_name(name):
    """Return the current version of the snippet with that name."""
    try:
        return SnippetVersion.query \
            .join(CurrentVersionAssociation) \
            .join(Snippet) \
                .filter(Snippet.party == g.party) \
                .filter(Snippet.name == name) \
            .one()
    except NoResultFound:
        raise SnippetNotFound(name)


class SnippetNotFound(Exception):

    def __init__(self, name):
        self.name = name
