# -*- coding: utf-8 -*-

"""
byceps.blueprints.tourney_admin.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ...database import db

from ..tourney.models.tourney_category import TourneyCategory


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


def get_categories_for_party(party):
    """Return the categories for this party."""
    return TourneyCategory.query \
        .for_party(party) \
        .order_by(TourneyCategory.position) \
        .all()
