"""
byceps.services.ticketing.category_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import Dict, Optional, Sequence

from ...database import db
from ...typing import PartyID

from .models.category import Category as DbCategory
from .models.ticket import Ticket as DbTicket
from .transfer.models import TicketCategory, TicketCategoryID


def create_category(party_id: PartyID, title: str) -> TicketCategory:
    """Create a category."""
    category = DbCategory(party_id, title)

    db.session.add(category)
    db.session.commit()

    return _db_entity_to_category(category)


def count_categories_for_party(party_id: PartyID) -> int:
    """Return the number of categories for that party."""
    return DbCategory.query \
        .for_party(party_id) \
        .count()


def find_category(category_id: TicketCategoryID) -> Optional[TicketCategory]:
    """Return the category with that ID, or `None` if not found."""
    category = DbCategory.query.get(category_id)

    return _db_entity_to_category(category)


def get_categories_for_party(party_id: PartyID) -> Sequence[TicketCategory]:
    """Return all categories for that party."""
    categories = DbCategory.query \
        .for_party(party_id) \
        .all()

    return [_db_entity_to_category(category) for category in categories]


def get_categories_with_ticket_counts_for_party(
    party_id: PartyID
) -> Dict[TicketCategory, int]:
    """Return all categories with ticket counts for that party."""
    category = db.aliased(DbCategory)

    subquery = db.session \
        .query(
            db.func.count(DbTicket.id)
        ) \
        .join(DbCategory) \
        .filter(DbCategory.id == category.id) \
        .filter(DbTicket.revoked == False) \
        .subquery() \
        .as_scalar()

    rows = db.session \
        .query(
            category,
            subquery
        ) \
        .filter(category.party_id == party_id) \
        .group_by(category.id) \
        .all()

    return {
        _db_entity_to_category(category): ticket_count
        for category, ticket_count in rows
    }


def _db_entity_to_category(category: DbCategory) -> TicketCategory:
    return TicketCategory(
        category.id,
        category.party_id,
        category.title,
    )
