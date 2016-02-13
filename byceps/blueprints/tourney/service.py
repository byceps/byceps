# -*- coding: utf-8 -*-

"""
byceps.blueprints.tourney.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ...database import db

from .models.match import MatchComment


def get_match_comments(match):
    """Return comments on the match, ordered chronologically."""
    return MatchComment.query \
        .for_match(match) \
        .options(
            db.joinedload(MatchComment.created_by),
        ) \
        .order_by(MatchComment.created_at) \
        .all()


def create_match_comment(match, creator, body):
    """Create a comment to a match."""
    match_comment = MatchComment(match, creator, body)
    db.session.add(match_comment)
    db.session.commit()
    return match_comment
