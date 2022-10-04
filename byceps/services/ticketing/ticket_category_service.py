"""
byceps.services.ticketing.ticket_category_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from typing import Optional, Sequence

from ...database import db
from ...typing import PartyID

from .dbmodels.category import DbCategory
from .dbmodels.ticket import DbTicket
from .transfer.models import TicketCategory, TicketCategoryID


def create_category(party_id: PartyID, title: str) -> TicketCategory:
    """Create a category."""
    db_category = DbCategory(party_id, title)

    db.session.add(db_category)
    db.session.commit()

    return _db_entity_to_category(db_category)


def update_category(
    category_id: TicketCategoryID, title: str
) -> TicketCategory:
    """Update a category."""
    db_category = db.session.get(DbCategory, category_id)

    if db_category is None:
        raise ValueError(f'Unknown category ID "{category_id}"')

    db_category.title = title

    db.session.commit()

    return _db_entity_to_category(db_category)


def delete_category(category_id: TicketCategoryID) -> None:
    """Delete a category."""
    db.session.query(DbCategory) \
        .filter_by(id=category_id) \
        .delete()
    db.session.commit()


def count_categories_for_party(party_id: PartyID) -> int:
    """Return the number of categories for that party."""
    return db.session \
        .query(DbCategory) \
        .filter_by(party_id=party_id) \
        .count()


def find_category(category_id: TicketCategoryID) -> Optional[TicketCategory]:
    """Return the category with that ID, or `None` if not found."""
    db_category = db.session.get(DbCategory, category_id)

    if db_category is None:
        return None

    return _db_entity_to_category(db_category)


def get_category(category_id: TicketCategoryID) -> TicketCategory:
    """Return the category with that ID, or raise an exception not found."""
    category = find_category(category_id)

    if category is None:
        raise ValueError(f'Unknown ticket category ID "{category_id}"')

    return category


def get_categories_for_party(party_id: PartyID) -> Sequence[TicketCategory]:
    """Return all categories for that party."""
    db_categories = db.session \
        .query(DbCategory) \
        .filter_by(party_id=party_id) \
        .all()

    return [
        _db_entity_to_category(db_category) for db_category in db_categories
    ]


def get_categories_with_ticket_counts_for_party(
    party_id: PartyID,
) -> dict[TicketCategory, int]:
    """Return all categories with ticket counts for that party."""
    category = db.aliased(DbCategory)

    subquery = db.session \
        .query(
            db.func.count(DbTicket.id)
        ) \
        .join(DbCategory) \
        .filter(DbCategory.id == category.id) \
        .filter(DbTicket.revoked == False) \
        .scalar_subquery()

    rows = db.session \
        .query(
            category,
            subquery
        ) \
        .filter(category.party_id == party_id) \
        .group_by(category.id) \
        .all()

    return {
        _db_entity_to_category(db_category): ticket_count
        for db_category, ticket_count in rows
    }


def _db_entity_to_category(db_category: DbCategory) -> TicketCategory:
    return TicketCategory(
        id=db_category.id,
        party_id=db_category.party_id,
        title=db_category.title,
    )
