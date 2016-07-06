# -*- coding: utf-8 -*-

"""
byceps.blueprints.snippet_admin.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from difflib import HtmlDiff

from ...database import db

from ..party.models import Party
from ..snippet.models.snippet import Snippet


def get_parties_with_snippet_counts():
    """Yield (party, snippet count) pairs."""
    parties = Party.query.all()

    snippet_counts_by_party_id = _get_snippet_counts_by_party_id()

    for party in parties:
        snippet_count = snippet_counts_by_party_id.get(party.id, 0)
        yield party, snippet_count


def _get_snippet_counts_by_party_id():
    return dict(db.session \
        .query(
            Snippet.party_id,
            db.func.count(Snippet.id)
        ) \
        .group_by(Snippet.party_id) \
        .all())


def create_html_diff(from_text, to_text, from_description, to_description,
                     *, numlines=3):
    """Calculate the difference between the two texts and render it as HTML."""
    from_lines = from_text.split('\n')
    to_lines = to_text.split('\n')

    return HtmlDiff().make_table(from_lines, to_lines,
                                 from_description, to_description,
                                 context=True, numlines=numlines)
