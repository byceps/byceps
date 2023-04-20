"""
byceps.services.tourney.tourney_category_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Optional

from sqlalchemy import delete, select

from byceps.database import db
from byceps.services.party.dbmodels.party import DbParty
from byceps.typing import PartyID

from .dbmodels.tourney_category import DbTourneyCategory
from .models import TourneyCategory, TourneyCategoryID


def create_category(party_id: PartyID, title: str) -> TourneyCategory:
    """Create a category for that party."""
    db_party = db.session.get(DbParty, party_id)
    if db_party is None:
        raise ValueError(f'Unknown party ID "{party_id}"')

    db_category = DbTourneyCategory(db_party.id, title)
    db_party.tourney_categories.append(db_category)

    db.session.commit()

    return _db_entity_to_category(db_category)


def update_category(
    category_id: TourneyCategoryID, title: str
) -> TourneyCategory:
    """Update category."""
    db_category = _get_db_category(category_id)

    db_category.title = title
    db.session.commit()

    return _db_entity_to_category(db_category)


def move_category_up(category_id: TourneyCategoryID) -> TourneyCategory:
    """Move a category upwards by one position."""
    db_category = _get_db_category(category_id)

    db_category_list = db_category.party.tourney_categories

    if db_category.position == 1:
        raise ValueError('Category already is at the top.')

    db_popped_category = db_category_list.pop(db_category.position - 1)
    db_category_list.insert(db_popped_category.position - 2, db_popped_category)

    db.session.commit()

    return _db_entity_to_category(db_category)


def move_category_down(category_id: TourneyCategoryID) -> TourneyCategory:
    """Move a category downwards by one position."""
    db_category = _get_db_category(category_id)

    db_category_list = db_category.party.tourney_categories

    if db_category.position == len(db_category_list):
        raise ValueError('Category already is at the bottom.')

    popped_category = db_category_list.pop(db_category.position - 1)
    db_category_list.insert(popped_category.position, popped_category)

    db.session.commit()

    return _db_entity_to_category(db_category)


def delete_category(category_id: TourneyCategoryID) -> None:
    """Delete a category."""
    category = get_category(category_id)

    db.session.execute(delete(DbTourneyCategory).filter_by(id=category.id))
    db.session.commit()


def find_category(category_id: TourneyCategoryID) -> Optional[TourneyCategory]:
    """Return the category with that id, or `None` if not found."""
    db_category = _find_db_category(category_id)

    if db_category is None:
        return None

    return _db_entity_to_category(db_category)


def get_category(category_id: TourneyCategoryID) -> TourneyCategory:
    """Return the category with that id, or raise an exception if not found."""
    category = find_category(category_id)

    if category is None:
        raise ValueError(f'Unknown tourney category ID "{category_id}"')

    return category


def _find_db_category(
    category_id: TourneyCategoryID,
) -> Optional[DbTourneyCategory]:
    return db.session.get(DbTourneyCategory, category_id)


def _get_db_category(category_id: TourneyCategoryID) -> DbTourneyCategory:
    db_category = _find_db_category(category_id)

    if db_category is None:
        raise ValueError(f'Unknown category ID "{category_id}"')

    return db_category


def get_categories_for_party(party_id: PartyID) -> list[TourneyCategory]:
    """Return the categories for this party."""
    db_categories = db.session.scalars(
        select(DbTourneyCategory)
        .filter_by(party_id=party_id)
        .order_by(DbTourneyCategory.position)
    ).all()

    return [
        _db_entity_to_category(db_category) for db_category in db_categories
    ]


def _db_entity_to_category(db_category: DbTourneyCategory) -> TourneyCategory:
    return TourneyCategory(
        id=db_category.id,
        party_id=db_category.party_id,
        position=db_category.position,
        title=db_category.title,
    )
