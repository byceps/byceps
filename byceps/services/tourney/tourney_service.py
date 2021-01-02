"""
byceps.services.tourney.tourney_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime
from typing import List, Optional

from ...database import db
from ...typing import PartyID, UserID

from . import category_service
from .models.participant import Participant as DbParticipant
from .models.tourney import Tourney as DbTourney
from .models.tourney_category import TourneyCategory as DbTourneyCategory
from .transfer.models import Tourney, TourneyCategoryID, TourneyID


def create_tourney(
    title: str,
    category_id: TourneyCategoryID,
    max_participant_count: int,
    starts_at: datetime,
    *,
    subtitle: Optional[str] = None,
    logo_url: Optional[str] = None,
) -> Tourney:
    """Create a tourney."""
    category = category_service.find_category(category_id)
    if category is None:
        raise ValueError(f'Unknown tourney category ID "{category_id}"')

    tourney = DbTourney(
        title,
        category.id,
        max_participant_count,
        starts_at,
        subtitle=subtitle,
        logo_url=logo_url,
    )

    db.session.add(tourney)
    db.session.commit()

    return _db_entity_to_tourney(tourney)


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
    tourney = _get_db_tourney(tourney_id)

    tourney.title = title
    tourney.subtitle = subtitle
    tourney.logo_url = logo_url
    tourney.category_id = category_id
    tourney.max_participant_count = max_participant_count
    tourney.starts_at = starts_at

    db.session.commit()

    return _db_entity_to_tourney(tourney)


def delete_tourney(tourney_id: TourneyID) -> None:
    """Delete a tourney."""
    tourney = get_tourney(tourney_id)

    db.session.query(DbTourney) \
        .filter_by(id=tourney_id) \
        .delete()

    db.session.commit()


def find_tourney(tourney_id: int) -> Optional[Tourney]:
    """Return the tourney with that id, or `None` if not found."""
    tourney = _find_db_tourney(tourney_id)

    if tourney is None:
        return None

    return _db_entity_to_tourney(tourney)


def _find_db_tourney(tourney_id: TourneyID) -> Optional[DbTourney]:
    return DbTourney.query.get(tourney_id)


def get_tourney(tourney_id: int) -> Tourney:
    """Return the tourney with that ID.

    Raise an exception if not found.
    """
    tourney = _find_tourney(tourney_id)

    if tourney is None:
        raise ValueError(f'Unknown tourney ID "{tourney_id}"')

    return tourney


def _get_db_tourney(tourney_id: int) -> DbTourney:
    tourney = _find_db_tourney(tourney_id)

    if tourney is None:
        raise ValueError(f'Unknown tourney ID "{tourney_id}"')

    return tourney


def get_tourneys_for_party(party_id: PartyID) -> List[Tourney]:
    """Return the tourneys for that party."""
    rows = db.session \
        .query(DbTourney, db.func.count(DbParticipant.id)) \
        .join(DbTourneyCategory) \
        .join(DbParticipant, isouter=True) \
        .filter(DbTourneyCategory.party_id == party_id) \
        .group_by(DbTourney.id) \
        .all()

    return [_db_entity_to_tourney(row[0], row[1]) for row in rows]


def _db_entity_to_tourney(
    tourney: DbTourney, current_participant_count: int = -1
) -> Tourney:
    return Tourney(
        id=tourney.id,
        title=tourney.title,
        subtitle=tourney.subtitle,
        logo_url=tourney.logo_url,
        category_id=tourney.category_id,
        current_participant_count=current_participant_count,
        max_participant_count=tourney.max_participant_count,
        starts_at=tourney.starts_at,
    )
