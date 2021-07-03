"""
byceps.services.tourney.tourney_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from datetime import datetime
from typing import Optional

from ...database import db
from ...typing import PartyID, UserID

from ..party import service as party_service

from . import category_service
from .dbmodels.participant import Participant as DbParticipant
from .dbmodels.tourney import Tourney as DbTourney
from .dbmodels.tourney_category import TourneyCategory as DbTourneyCategory
from .transfer.models import (
    Tourney,
    TourneyCategoryID,
    TourneyID,
    TourneyWithCategory,
)


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

    category = category_service.find_category(category_id)
    if category is None:
        raise ValueError(f'Unknown tourney category ID "{category_id}"')

    tourney = DbTourney(
        party.id,
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


def find_tourney(tourney_id: TourneyID) -> Optional[Tourney]:
    """Return the tourney with that id, or `None` if not found."""
    tourney = _find_db_tourney(tourney_id)

    if tourney is None:
        return None

    return _db_entity_to_tourney(tourney)


def _find_db_tourney(tourney_id: TourneyID) -> Optional[DbTourney]:
    return db.session.query(DbTourney).get(tourney_id)


def get_tourney(tourney_id: TourneyID) -> Tourney:
    """Return the tourney with that ID.

    Raise an exception if not found.
    """
    tourney = find_tourney(tourney_id)

    if tourney is None:
        raise ValueError(f'Unknown tourney ID "{tourney_id}"')

    return tourney


def _get_db_tourney(tourney_id: TourneyID) -> DbTourney:
    tourney = _find_db_tourney(tourney_id)

    if tourney is None:
        raise ValueError(f'Unknown tourney ID "{tourney_id}"')

    return tourney


def get_tourneys_for_party(party_id: PartyID) -> list[TourneyWithCategory]:
    """Return the tourneys for that party."""
    rows = db.session \
        .query(DbTourney, DbTourneyCategory, db.func.count(DbParticipant.id)) \
        .join(DbTourneyCategory) \
        .join(DbParticipant, isouter=True) \
        .filter(DbTourney.party_id == party_id) \
        .group_by(DbTourney.id, DbTourneyCategory) \
        .all()

    return [_to_tourney_with_category(row[0], row[1], row[2]) for row in rows]


def _db_entity_to_tourney(
    tourney: DbTourney,
    current_participant_count: int = -1,
) -> Tourney:
    return Tourney(
        id=tourney.id,
        party_id=tourney.party_id,
        title=tourney.title,
        subtitle=tourney.subtitle,
        logo_url=tourney.logo_url,
        category_id=tourney.category_id,
        current_participant_count=current_participant_count,
        max_participant_count=tourney.max_participant_count,
        starts_at=tourney.starts_at,
    )


def _to_tourney_with_category(
    db_tourney: DbTourney,
    db_category: DbTourneyCategory,
    current_participant_count: int = -1,
) -> TourneyWithCategory:
    tourney = _db_entity_to_tourney(db_tourney, current_participant_count)
    category = category_service._db_entity_to_category(db_category)

    return TourneyWithCategory.from_tourney_and_category(
        tourney, category, current_participant_count
    )
