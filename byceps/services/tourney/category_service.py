"""
byceps.services.tourney.category_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from typing import Optional

from ...database import db
from ...typing import PartyID

from ..party.dbmodels.party import Party as DbParty

from .dbmodels.tourney_category import TourneyCategory as DbTourneyCategory
from .transfer.models import TourneyCategory, TourneyCategoryID


def create_category(party_id: PartyID, title: str) -> TourneyCategory:
    """Create a category for that party."""
    party = db.session.query(DbParty).get(party_id)
    if party is None:
        raise ValueError(f'Unknown party ID "{party_id}"')

    category = DbTourneyCategory(party.id, title)
    party.tourney_categories.append(category)

    db.session.commit()

    return _db_entity_to_category(category)


def update_category(
    category_id: TourneyCategoryID, title: str
) -> TourneyCategory:
    """Update category."""
    category = _get_db_category(category_id)

    category.title = title
    db.session.commit()

    return _db_entity_to_category(category)


def move_category_up(category_id: TourneyCategoryID) -> TourneyCategory:
    """Move a category upwards by one position."""
    category = _get_db_category(category_id)

    category_list = category.party.tourney_categories

    if category.position == 1:
        raise ValueError('Category already is at the top.')

    popped_category = category_list.pop(category.position - 1)
    category_list.insert(popped_category.position - 2, popped_category)

    db.session.commit()

    return _db_entity_to_category(category)


def move_category_down(category_id: TourneyCategoryID) -> TourneyCategory:
    """Move a category downwards by one position."""
    category = _get_db_category(category_id)

    category_list = category.party.tourney_categories

    if category.position == len(category_list):
        raise ValueError('Category already is at the bottom.')

    popped_category = category_list.pop(category.position - 1)
    category_list.insert(popped_category.position, popped_category)

    db.session.commit()

    return _db_entity_to_category(category)


def delete_category(category_id: TourneyCategoryID) -> None:
    """Delete a category."""
    category = get_category(category_id)

    db.session.query(DbTourneyCategory) \
        .filter_by(id=category_id) \
        .delete()

    db.session.commit()


def find_category(category_id: TourneyCategoryID) -> Optional[TourneyCategory]:
    """Return the category with that id, or `None` if not found."""
    category = _find_db_category(category_id)

    if category is None:
        return None

    return _db_entity_to_category(category)


def get_category(category_id: TourneyCategoryID) -> TourneyCategory:
    """Return the category with that id, or raise an exception if not found."""
    category = find_category(category_id)

    if category is None:
        raise ValueError(f'Unknown tourney category ID "{category_id}"')

    return category


def _find_db_category(
    category_id: TourneyCategoryID,
) -> Optional[DbTourneyCategory]:
    return db.session.query(DbTourneyCategory).get(category_id)


def _get_db_category(category_id: TourneyCategoryID) -> DbTourneyCategory:
    category = _find_db_category(category_id)

    if category is None:
        raise ValueError(f'Unknown category ID "{category_id}"')

    return category


def get_categories_for_party(party_id: PartyID) -> list[TourneyCategory]:
    """Return the categories for this party."""
    categories = db.session \
        .query(DbTourneyCategory) \
        .filter_by(party_id=party_id) \
        .order_by(DbTourneyCategory.position) \
        .all()

    return [_db_entity_to_category(category) for category in categories]


def _db_entity_to_category(category: DbTourneyCategory) -> TourneyCategory:
    return TourneyCategory(
        id=category.id,
        party_id=category.party_id,
        position=category.position,
        title=category.title,
    )
