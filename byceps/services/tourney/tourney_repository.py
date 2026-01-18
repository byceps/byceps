"""
byceps.services.tourney.tourney_repository
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections.abc import Sequence
from datetime import datetime

from sqlalchemy import delete, select

from byceps.database import db
from byceps.services.party.models import PartyID

from .dbmodels.participant import DbParticipant
from .dbmodels.tourney import DbTourney
from .dbmodels.tourney_category import DbTourneyCategory
from .models import Tourney, TourneyCategoryID, TourneyID


def create_tourney(tourney: Tourney) -> None:
    """Create a tourney."""
    db_tourney = DbTourney(
        tourney.id,
        tourney.party_id,
        tourney.title,
        tourney.category_id,
        tourney.team_size,
        tourney.max_participant_count,
        tourney.starts_at,
        subtitle=tourney.subtitle,
        logo_url=tourney.logo_url,
        registration_open=tourney.registration_open,
    )

    db.session.add(db_tourney)
    db.session.commit()


def update_tourney(
    tourney_id: TourneyID,
    title: str,
    subtitle: str | None,
    logo_url: str | None,
    category_id: TourneyCategoryID,
    max_participant_count: int,
    starts_at: datetime,
) -> DbTourney:
    """Update tourney."""
    db_tourney = get_tourney(tourney_id)

    db_tourney.title = title
    db_tourney.subtitle = subtitle
    db_tourney.logo_url = logo_url
    db_tourney.category_id = category_id
    db_tourney.max_participant_count = max_participant_count
    db_tourney.starts_at = starts_at

    db.session.commit()

    return db_tourney


def open_registration(tourney: Tourney) -> None:
    """Open the registration for a tourney."""
    db_tourney = get_tourney(tourney.id)
    db_tourney.registration_open = tourney.registration_open
    db.session.commit()


def close_registration(tourney: Tourney) -> None:
    """Close the registration for a tourney."""
    db_tourney = get_tourney(tourney.id)
    db_tourney.registration_open = tourney.registration_open
    db.session.commit()


def delete_tourney(tourney_id: TourneyID) -> None:
    """Delete a tourney."""
    db.session.execute(delete(DbTourney).filter_by(id=tourney_id))
    db.session.commit()


def find_tourney(tourney_id: TourneyID) -> DbTourney | None:
    """Return the tourney with that id, or `None` if not found."""
    return db.session.get(DbTourney, tourney_id)


def get_tourney(tourney_id: TourneyID) -> DbTourney:
    """Return the tourney with that ID.

    Raise an exception if not found.
    """
    db_tourney = find_tourney(tourney_id)

    if db_tourney is None:
        raise ValueError(f'Unknown tourney ID "{tourney_id}"')

    return db_tourney


def find_tourney_with_category(
    tourney_id: TourneyID,
) -> tuple[DbTourney, DbTourneyCategory, int] | None:
    """Return the tourney with that id, with categories and participant
    counts, or `None` if not found.
    """
    return (
        db.session.execute(
            select(
                DbTourney, DbTourneyCategory, db.func.count(DbParticipant.id)
            )
            .join(DbTourneyCategory)
            .join(DbParticipant, isouter=True)
            .filter(DbTourney.id == tourney_id)
            .group_by(DbTourney.id, DbTourneyCategory)
        )
        .tuples()
        .one_or_none()
    )


def get_tourneys_for_party(
    party_id: PartyID,
) -> Sequence[tuple[DbTourney, DbTourneyCategory, int]]:
    """Return the tourneys for that party, with categories and participant counts."""
    return (
        db.session.execute(
            select(
                DbTourney, DbTourneyCategory, db.func.count(DbParticipant.id)
            )
            .join(DbTourneyCategory)
            .join(DbParticipant, isouter=True)
            .filter(DbTourney.party_id == party_id)
            .group_by(DbTourney.id, DbTourneyCategory)
        )
        .tuples()
        .all()
    )
