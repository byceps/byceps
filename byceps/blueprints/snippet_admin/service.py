# -*- coding: utf-8 -*-

"""
byceps.blueprints.snippet_admin.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from difflib import HtmlDiff

from ...database import db

from ..snippet.models.snippet import Snippet


def get_snippets_for_party(party):
    """Return all snippets for that party."""
    return Snippet.query \
        .for_party(party) \
        .order_by(Snippet.name) \
        .all()


def get_snippets_for_party_with_current_versions(party):
    """Return all snippets with their current versions for that party."""
    return Snippet.query \
        .for_party(party) \
        .options(
            db.joinedload('current_version_association').joinedload('version')
        ) \
        .all()


def create_html_diff(from_text, to_text, from_description, to_description,
                     *, numlines=3):
    """Calculate the difference between the two texts and render it as HTML.

    If the texts to compare are equal, `None` is returned.
    """
    from_text = _fallback_if_none(from_text)
    to_text = _fallback_if_none(to_text)

    if from_text == to_text:
        return None

    from_lines = from_text.split('\n')
    to_lines = to_text.split('\n')

    return HtmlDiff().make_table(from_lines, to_lines,
                                 from_description, to_description,
                                 context=True, numlines=numlines)


def _fallback_if_none(value, fallback=''):
    return value if (value is not None) else fallback
