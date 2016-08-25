# -*- coding: utf-8 -*-

"""
byceps.blueprints.seating.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ...database import db

from .models.area import Area
from .models.category import Category


def find_area_for_party_by_slug(party, slug):
    """Return the area for that party with that slug, or `None` if not found."""
    return Area.query \
        .for_party(party) \
        .filter_by(slug=slug) \
        .options(db.joinedload('seats').joinedload('category')) \
        .first()


def get_areas_for_party(party):
    """Return all areas for that party."""
    return Area.query \
        .for_party(party) \
        .all()


def get_categories_for_party(party):
    """Return all categories for that party."""
    return Category.query \
        .for_party(party) \
        .all()
