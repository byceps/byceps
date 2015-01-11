# -*- coding: utf-8 -*-

"""
byceps.blueprints.tourney.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2015 Jochen Kupperschmidt
"""

from ...database import db

from .models import MatchComment


def get_match_comments(match):
    """Return comments on the match, ordered chronologically."""
    return MatchComment.query \
        .for_match(match) \
        .options(
            db.joinedload(MatchComment.created_by),
        ) \
        .order_by(MatchComment.created_at) \
        .all()
