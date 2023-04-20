"""
byceps.services.tourney.tourney_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import delete, select

from byceps.database import db
from byceps.services.party import party_service
from byceps.typing import PartyID

from . import tourney_category_service
from .dbmodels.participant import DbParticipant
from .dbmodels.tourney import DbTourney
from .dbmodels.tourney_category import DbTourneyCategory
from .models import Tourney, TourneyCategoryID, TourneyID, TourneyWithCategory


def create_tourney(
    party_id: PartyID,
    title: str,
    category_id: TourneyCategoryID,
    max_participant_count: int,
    starts_at: datetime,
    *,
    subtitle: Optional[str] = None,
    logo_url: Optional[str] = None,
) -> Tourney:
    """Create a tourney."""
    party = party_service.get_party(party_id)
    category = tourney_category_service.get_category(category_id)

    db_tourney = DbTourney(
        party.id,
        title,
        category.id,
        max_participant_count,
        starts_at,
        subtitle=subtitle,
        logo_url=logo_url,
    )

    db.session.add(db_tourney)
    db.session.commit()

    return _db_entity_to_tourney(db_tourney)


def update_tourney(
    tourney_id: TourneyID,
    title: str,
    subtitle: Optional[str],
    logo_url: Optional[str],
    category_id: TourneyCategoryID,
    max_participant_count: int,
    starts_at: datetime,
) -> Tourney:
    """Update tourney."""
    db_tourney = _get_db_tourney(tourney_id)

    db_tourney.title = title
    db_tourney.subtitle = subtitle
    db_tourney.logo_url = logo_url
    db_tourney.category_id = category_id
    db_tourney.max_participant_count = max_participant_count
    db_tourney.starts_at = starts_at

    db.session.commit()

    return _db_entity_to_tourney(db_tourney)


def delete_tourney(tourney_id: TourneyID) -> None:
    """Delete a tourney."""
    tourney = get_tourney(tourney_id)

    db.session.execute(delete(DbTourney).filter_by(id=tourney.id))
    db.session.commit()


def find_tourney(tourney_id: TourneyID) -> Optional[Tourney]:
    """Return the tourney with that id, or `None` if not found."""
    db_tourney = _find_db_tourney(tourney_id)

    if db_tourney is None:
        return None

    return _db_entity_to_tourney(db_tourney)


def _find_db_tourney(tourney_id: TourneyID) -> Optional[DbTourney]:
    return db.session.get(DbTourney, tourney_id)


def get_tourney(tourney_id: TourneyID) -> Tourney:
    """Return the tourney with that ID.

    Raise an exception if not found.
    """
    tourney = find_tourney(tourney_id)

    if tourney is None:
        raise ValueError(f'Unknown tourney ID "{tourney_id}"')

    return tourney


def _get_db_tourney(tourney_id: TourneyID) -> DbTourney:
    db_tourney = _find_db_tourney(tourney_id)

    if db_tourney is None:
        raise ValueError(f'Unknown tourney ID "{tourney_id}"')

    return db_tourney


def get_tourneys_for_party(party_id: PartyID) -> list[TourneyWithCategory]:
    """Return the tourneys for that party."""
    rows = db.session.execute(
        select(DbTourney, DbTourneyCategory, db.func.count(DbParticipant.id))
        .join(DbTourneyCategory)
        .join(DbParticipant, isouter=True)
        .filter(DbTourney.party_id == party_id)
        .group_by(DbTourney.id, DbTourneyCategory)
    ).all()

    return [
        _to_tourney_with_category(db_tourney, db_category, participant_count)
        for db_tourney, db_category, participant_count in rows
    ]


def _db_entity_to_tourney(
    db_tourney: DbTourney,
    current_participant_count: int = -1,
) -> Tourney:
    return Tourney(
        id=db_tourney.id,
        party_id=db_tourney.party_id,
        title=db_tourney.title,
        subtitle=db_tourney.subtitle,
        logo_url=db_tourney.logo_url,
        category_id=db_tourney.category_id,
        current_participant_count=current_participant_count,
        max_participant_count=db_tourney.max_participant_count,
        starts_at=db_tourney.starts_at,
    )


def _to_tourney_with_category(
    db_tourney: DbTourney,
    db_category: DbTourneyCategory,
    current_participant_count: int = -1,
) -> TourneyWithCategory:
    db_tourney = _db_entity_to_tourney(db_tourney, current_participant_count)
    category = tourney_category_service._db_entity_to_category(db_category)

    return TourneyWithCategory.from_tourney_and_category(
        db_tourney, category, current_participant_count
    )
