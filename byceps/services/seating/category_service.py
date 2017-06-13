"""
byceps.services.seating.category_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import Sequence

from ...database import db
from ...typing import PartyID

from .models.category import Category


def create_category(party_id: PartyID, title: str) -> Category:
    """Create a category."""
    category = Category(party_id, title)

    db.session.add(category)
    db.session.commit()

    return category


def count_categories_for_party(party_id: PartyID) -> int:
    """Return the number of categories for that party."""
    return Category.query \
        .for_party_id(party_id) \
        .count()


def get_categories_for_party(party_id: PartyID) -> Sequence[Category]:
    """Return all categories for that party."""
    return Category.query \
        .for_party_id(party_id) \
        .all()
