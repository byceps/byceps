"""
byceps.services.ticketing.category_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import Optional, Sequence

from ...database import db
from ...typing import PartyID

from .models.category import Category as DbCategory
from .transfer.models import TicketCategoryID


def create_category(party_id: PartyID, title: str) -> DbCategory:
    """Create a category."""
    category = DbCategory(party_id, title)

    db.session.add(category)
    db.session.commit()

    return category


def count_categories_for_party(party_id: PartyID) -> int:
    """Return the number of categories for that party."""
    return DbCategory.query \
        .for_party(party_id) \
        .count()


def find_category(category_id: TicketCategoryID) -> Optional[DbCategory]:
    """Return the category with that ID, or `None` if not found."""
    return DbCategory.query.get(category_id)


def get_categories_for_party(party_id: PartyID) -> Sequence[DbCategory]:
    """Return all categories for that party."""
    return DbCategory.query \
        .for_party(party_id) \
        .all()
