# -*- coding: utf-8 -*-

"""
byceps.services.tourney.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ...database import db

from .models.match import Match, MatchComment
from .models.tourney_category import TourneyCategory


# -------------------------------------------------------------------- #
# tourney categories


def create_category(party, title):
    """Create a category for that party."""
    category = TourneyCategory(party, title)
    party.tourney_categories.append(category)

    db.session.commit()

    return category


def update_category(category, title):
    """Update category."""
    category.title = title
    db.session.commit()


def move_category_up(category):
    """Move a category upwards by one position."""
    category_list = category.party.tourney_categories

    if category.position == 1:
        raise ValueError('Category already is at the top.')

    popped_category = category_list.pop(category.position - 1)
    category_list.insert(popped_category.position - 2, popped_category)

    db.session.commit()


def move_category_down(category):
    """Move a category downwards by one position."""
    category_list = category.party.tourney_categories

    if category.position == len(category_list):
        raise ValueError('Category already is at the bottom.')

    popped_category = category_list.pop(category.position - 1)
    category_list.insert(popped_category.position, popped_category)

    db.session.commit()


def find_tourney_category(category_id):
    """Return the category with that id, or `None` if not found."""
    return TourneyCategory.query.get(category_id)


def get_categories_for_party(party):
    """Return the categories for this party."""
    return TourneyCategory.query \
        .filter_by(party_id=party.id) \
        .order_by(TourneyCategory.position) \
        .all()


# -------------------------------------------------------------------- #
# matches


def get_match_comments(match):
    """Return comments on the match, ordered chronologically."""
    return MatchComment.query \
        .for_match(match) \
        .options(
            db.joinedload(MatchComment.created_by),
        ) \
        .order_by(MatchComment.created_at) \
        .all()


def create_match_comment(match, creator_id, body):
    """Create a comment to a match."""
    match_comment = MatchComment(match, creator_id, body)

    db.session.add(match_comment)
    db.session.commit()

    return match_comment


def find_match(match_id):
    """Return the match with that id, or `None` if not found."""
    return Match.query.get(match_id)
